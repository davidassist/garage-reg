/**
 * Queue Manager - Handles background sync queue operations
 * Manages retry logic and queue processing
 */

import { QueueItem, QueueItemType, QueueAction, QueueItemStatus } from '../types'
import { DatabaseManager } from '../storage/database'

export interface QueueOptions {
  maxRetries?: number
  retryDelayMs?: number
  batchSize?: number
}

export class QueueManager {
  private db = DatabaseManager.getInstance()
  private isProcessing = false
  private defaultOptions: Required<QueueOptions> = {
    maxRetries: 3,
    retryDelayMs: 5000, // 5 seconds
    batchSize: 10
  }

  /**
   * Add item to sync queue
   */
  public async addToQueue(
    type: QueueItemType,
    entityId: string,
    action: QueueAction,
    data: any,
    priority = 1
  ): Promise<string> {
    const item: QueueItem = {
      id: `queue_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      entityId,
      action,
      data,
      priority,
      attempts: 0,
      maxAttempts: this.defaultOptions.maxRetries,
      createdAt: new Date().toISOString(),
      scheduledAt: new Date().toISOString(),
      status: 'pending'
    }

    const sql = `
      INSERT INTO sync_queue (
        id, type, entity_id, action, data, priority,
        attempts, max_attempts, created_at, scheduled_at, status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `

    await this.db.executeSql(sql, [
      item.id,
      item.type,
      item.entityId,
      item.action,
      JSON.stringify(item.data),
      item.priority,
      item.attempts,
      item.maxAttempts,
      item.createdAt,
      item.scheduledAt,
      item.status
    ])

    return item.id
  }

  /**
   * Get pending queue items
   */
  public async getPendingItems(limit?: number): Promise<QueueItem[]> {
    const sql = `
      SELECT * FROM sync_queue 
      WHERE status = 'pending' AND scheduled_at <= ?
      ORDER BY priority DESC, created_at ASC
      ${limit ? `LIMIT ${limit}` : ''}
    `
    
    const result = await this.db.executeSql(sql, [new Date().toISOString()])
    
    const items: QueueItem[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      items.push(this.mapRowToQueueItem(result[0].rows.item(i)))
    }
    
    return items
  }

  /**
   * Get all queue items with optional filter
   */
  public async getQueueItems(status?: QueueItemStatus): Promise<QueueItem[]> {
    let sql = 'SELECT * FROM sync_queue'
    const params: any[] = []
    
    if (status) {
      sql += ' WHERE status = ?'
      params.push(status)
    }
    
    sql += ' ORDER BY created_at DESC'
    
    const result = await this.db.executeSql(sql, params)
    
    const items: QueueItem[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      items.push(this.mapRowToQueueItem(result[0].rows.item(i)))
    }
    
    return items
  }

  /**
   * Update queue item status
   */
  public async updateItemStatus(
    id: string,
    status: QueueItemStatus,
    errorMessage?: string
  ): Promise<void> {
    let sql = 'UPDATE sync_queue SET status = ?'
    const params: any[] = [status]
    
    if (errorMessage) {
      sql += ', error_message = ?'
      params.push(errorMessage)
    }
    
    if (status === 'failed' || status === 'completed') {
      sql += ', last_attempt_at = ?'
      params.push(new Date().toISOString())
    }
    
    sql += ' WHERE id = ?'
    params.push(id)
    
    await this.db.executeSql(sql, params)
  }

  /**
   * Increment retry attempts for failed item
   */
  public async incrementAttempts(id: string): Promise<boolean> {
    // Get current item
    const result = await this.db.executeSql(
      'SELECT attempts, max_attempts FROM sync_queue WHERE id = ?',
      [id]
    )
    
    if (result[0].rows.length === 0) {
      return false
    }
    
    const item = result[0].rows.item(0)
    const newAttempts = item.attempts + 1
    
    if (newAttempts >= item.max_attempts) {
      // Max attempts reached, mark as failed
      await this.updateItemStatus(id, 'failed', 'Max retry attempts exceeded')
      return false
    }
    
    // Schedule for retry with exponential backoff
    const delayMs = this.defaultOptions.retryDelayMs * Math.pow(2, newAttempts - 1)
    const scheduledAt = new Date(Date.now() + delayMs).toISOString()
    
    await this.db.executeSql(
      `UPDATE sync_queue 
       SET attempts = ?, status = 'pending', scheduled_at = ?, last_attempt_at = ?
       WHERE id = ?`,
      [newAttempts, scheduledAt, new Date().toISOString(), id]
    )
    
    return true
  }

  /**
   * Remove completed items from queue
   */
  public async cleanupCompleted(): Promise<number> {
    const result = await this.db.executeSql(
      "DELETE FROM sync_queue WHERE status = 'completed'",
      []
    )
    
    return result[0].rowsAffected
  }

  /**
   * Remove old failed items from queue
   */
  public async cleanupFailed(olderThanDays = 7): Promise<number> {
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - olderThanDays)
    
    const result = await this.db.executeSql(
      "DELETE FROM sync_queue WHERE status = 'failed' AND created_at < ?",
      [cutoffDate.toISOString()]
    )
    
    return result[0].rowsAffected
  }

  /**
   * Get queue statistics
   */
  public async getQueueStats(): Promise<{
    pending: number
    processing: number
    completed: number
    failed: number
    total: number
  }> {
    const result = await this.db.executeSql(
      `SELECT 
        status,
        COUNT(*) as count
       FROM sync_queue
       GROUP BY status`,
      []
    )
    
    const stats = {
      pending: 0,
      processing: 0,
      completed: 0,
      failed: 0,
      total: 0
    }
    
    for (let i = 0; i < result[0].rows.length; i++) {
      const row = result[0].rows.item(i)
      stats[row.status as keyof typeof stats] = row.count
      stats.total += row.count
    }
    
    return stats
  }

  /**
   * Process queue items (called by sync service)
   */
  public async processQueue(
    processor: (item: QueueItem) => Promise<boolean>,
    options?: QueueOptions
  ): Promise<{
    processed: number
    successful: number
    failed: number
  }> {
    if (this.isProcessing) {
      throw new Error('Queue processing already in progress')
    }
    
    this.isProcessing = true
    
    try {
      const opts = { ...this.defaultOptions, ...options }
      const items = await this.getPendingItems(opts.batchSize)
      
      let processed = 0
      let successful = 0
      let failed = 0
      
      for (const item of items) {
        try {
          // Mark as processing
          await this.updateItemStatus(item.id, 'processing')
          
          // Process the item
          const success = await processor(item)
          
          if (success) {
            await this.updateItemStatus(item.id, 'completed')
            successful++
          } else {
            // Retry or fail
            const canRetry = await this.incrementAttempts(item.id)
            if (!canRetry) {
              failed++
            }
          }
          
          processed++
          
        } catch (error) {
          // Handle processing error
          const errorMessage = error instanceof Error ? error.message : 'Unknown error'
          const canRetry = await this.incrementAttempts(item.id)
          
          if (!canRetry) {
            await this.updateItemStatus(item.id, 'failed', errorMessage)
            failed++
          }
          
          processed++
        }
      }
      
      return { processed, successful, failed }
      
    } finally {
      this.isProcessing = false
    }
  }

  /**
   * Clear entire queue (use with caution)
   */
  public async clearQueue(): Promise<number> {
    const result = await this.db.executeSql('DELETE FROM sync_queue', [])
    return result[0].rowsAffected
  }

  /**
   * Map database row to QueueItem
   */
  private mapRowToQueueItem(row: any): QueueItem {
    return {
      id: row.id,
      type: row.type,
      entityId: row.entity_id,
      action: row.action,
      data: JSON.parse(row.data || '{}'),
      priority: row.priority,
      attempts: row.attempts,
      maxAttempts: row.max_attempts,
      createdAt: row.created_at,
      scheduledAt: row.scheduled_at,
      lastAttemptAt: row.last_attempt_at,
      errorMessage: row.error_message,
      status: row.status
    }
  }
}