/**
 * Delta Sync Service - Bidirectional synchronization with conflict resolution
 * Implements operational transform and last-write-wins policies
 */

import AsyncStorage from '@react-native-async-storage/async-storage'
import { DatabaseManager } from '../storage/database'
import { APIService } from './apiService'
import {
  DeltaOperation,
  SyncBatch,
  DeltaSyncResult,
  DeltaConflict,
  SyncPolicy,
  ConflictResolutionStrategy,
  Gate,
  Inspection
} from '../types'

export class DeltaSyncService {
  private static instance: DeltaSyncService
  private db = DatabaseManager.getInstance()
  private apiService = new APIService()
  
  // Default sync policy
  private defaultPolicy: SyncPolicy = {
    batchSize: 50,
    maxRetries: 3,
    retryDelayMs: 1000,
    maxRetryDelayMs: 30000,
    backoffMultiplier: 2,
    conflictResolution: 'last_write_wins',
    enableOperationalTransform: false
  }

  public static getInstance(): DeltaSyncService {
    if (!DeltaSyncService.instance) {
      DeltaSyncService.instance = new DeltaSyncService()
    }
    return DeltaSyncService.instance
  }

  /**
   * Record a delta operation for later sync
   */
  public async recordOperation(
    entityType: string,
    entityId: string,
    operationType: 'create' | 'update' | 'delete',
    fieldName?: string,
    oldValue?: any,
    newValue?: any,
    userId?: string
  ): Promise<string> {
    const operation: DeltaOperation = {
      id: `delta_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      entityType: entityType as any,
      entityId,
      operationType,
      fieldName,
      oldValue,
      newValue,
      rowVersion: await this.getNextRowVersion(entityType, entityId),
      timestamp: new Date().toISOString(),
      userId,
      syncStatus: 'pending'
    }

    const sql = `
      INSERT INTO delta_operations (
        id, entity_type, entity_id, operation_type, field_name,
        old_value, new_value, row_version, timestamp, user_id, sync_status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `

    await this.db.executeSql(sql, [
      operation.id,
      operation.entityType,
      operation.entityId,
      operation.operationType,
      operation.fieldName || null,
      operation.oldValue ? JSON.stringify(operation.oldValue) : null,
      operation.newValue ? JSON.stringify(operation.newValue) : null,
      operation.rowVersion,
      operation.timestamp,
      operation.userId || null,
      operation.syncStatus
    ])

    // Update entity row version
    await this.updateEntityVersion(entityType, entityId, operation.rowVersion)

    return operation.id
  }

  /**
   * Get next row version for entity
   */
  private async getNextRowVersion(entityType: string, entityId: string): Promise<number> {
    const tableName = this.getTableName(entityType)
    const sql = `SELECT row_version FROM ${tableName} WHERE id = ?`
    
    try {
      const result = await this.db.executeSql(sql, [entityId])
      if (result[0].rows.length > 0) {
        return result[0].rows.item(0).row_version + 1
      }
    } catch (error) {
      // Entity doesn't exist yet, start at 1
    }
    
    return 1
  }

  /**
   * Update entity row version
   */
  private async updateEntityVersion(entityType: string, entityId: string, rowVersion: number): Promise<void> {
    const tableName = this.getTableName(entityType)
    const etag = this.generateETag(entityId, rowVersion)
    
    const sql = `
      UPDATE ${tableName} 
      SET row_version = ?, etag = ?, updated_at = ?
      WHERE id = ?
    `
    
    await this.db.executeSql(sql, [
      rowVersion,
      etag,
      new Date().toISOString(),
      entityId
    ])
  }

  /**
   * Generate ETag for versioning
   */
  private generateETag(entityId: string, rowVersion: number): string {
    const timestamp = Date.now()
    return `"${entityId}-${rowVersion}-${timestamp}"`
  }

  /**
   * Get table name from entity type
   */
  private getTableName(entityType: string): string {
    const tableMap: Record<string, string> = {
      'gate': 'gates',
      'inspection': 'inspections',
      'photo': 'inspection_photos',
      'template': 'checklist_templates'
    }
    return tableMap[entityType] || entityType
  }

  /**
   * Push local changes to server (batch upload)
   */
  public async pushChanges(policy?: Partial<SyncPolicy>): Promise<DeltaSyncResult> {
    const syncPolicy = { ...this.defaultPolicy, ...policy }
    const batchId = `push_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // Create sync batch record
    await this.createSyncBatch(batchId, 'push', syncPolicy.batchSize)

    try {
      // Get pending operations
      const pendingOps = await this.getPendingOperations(syncPolicy.batchSize)
      
      if (pendingOps.length === 0) {
        return {
          success: true,
          batchId,
          syncedOperations: 0,
          conflicts: [],
          errors: []
        }
      }

      // Send batch to server
      const response = await this.apiService.pushDeltaBatch({
        batchId,
        operations: pendingOps,
        lastSyncToken: await this.getLastSyncToken()
      })

      // Process response
      const result = await this.processPushResponse(batchId, response, pendingOps, syncPolicy)
      
      // Update batch status
      await this.updateSyncBatchStatus(batchId, 'completed', result.syncedOperations, result.conflicts.length)

      return result

    } catch (error) {
      await this.updateSyncBatchStatus(batchId, 'failed', 0, 0, error instanceof Error ? error.message : 'Unknown error')
      throw error
    }
  }

  /**
   * Pull changes from server (batch download)
   */
  public async pullChanges(policy?: Partial<SyncPolicy>): Promise<DeltaSyncResult> {
    const syncPolicy = { ...this.defaultPolicy, ...policy }
    const batchId = `pull_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    await this.createSyncBatch(batchId, 'pull', syncPolicy.batchSize)

    try {
      const lastSyncToken = await this.getLastSyncToken()
      
      // Request changes from server
      const response = await this.apiService.pullDeltaBatch({
        batchId,
        lastSyncToken,
        batchSize: syncPolicy.batchSize
      })

      // Process incoming changes
      const result = await this.processPullResponse(batchId, response, syncPolicy)
      
      // Save new sync token
      if (response.nextSyncToken) {
        await this.saveLastSyncToken(response.nextSyncToken)
      }

      await this.updateSyncBatchStatus(batchId, 'completed', result.syncedOperations, result.conflicts.length)
      
      return result

    } catch (error) {
      await this.updateSyncBatchStatus(batchId, 'failed', 0, 0, error instanceof Error ? error.message : 'Unknown error')
      throw error
    }
  }

  /**
   * Get pending local operations
   */
  private async getPendingOperations(limit: number): Promise<DeltaOperation[]> {
    const sql = `
      SELECT * FROM delta_operations 
      WHERE sync_status = 'pending'
      ORDER BY timestamp ASC
      LIMIT ?
    `
    
    const result = await this.db.executeSql(sql, [limit])
    const operations: DeltaOperation[] = []
    
    for (let i = 0; i < result[0].rows.length; i++) {
      const row = result[0].rows.item(i)
      operations.push({
        id: row.id,
        entityType: row.entity_type,
        entityId: row.entity_id,
        operationType: row.operation_type,
        fieldName: row.field_name,
        oldValue: row.old_value ? JSON.parse(row.old_value) : undefined,
        newValue: row.new_value ? JSON.parse(row.new_value) : undefined,
        rowVersion: row.row_version,
        timestamp: row.timestamp,
        userId: row.user_id,
        syncStatus: row.sync_status,
        batchId: row.batch_id
      })
    }
    
    return operations
  }

  /**
   * Process push response from server
   */
  private async processPushResponse(
    batchId: string,
    response: any,
    operations: DeltaOperation[],
    policy: SyncPolicy
  ): Promise<DeltaSyncResult> {
    const result: DeltaSyncResult = {
      success: true,
      batchId,
      syncedOperations: 0,
      conflicts: [],
      errors: []
    }

    for (const operation of operations) {
      const serverResponse = response.results?.find((r: any) => r.operationId === operation.id)
      
      if (serverResponse?.success) {
        // Mark as synced
        await this.markOperationSynced(operation.id, serverResponse.serverVersion)
        result.syncedOperations++
      } else if (serverResponse?.conflict) {
        // Handle conflict
        const conflict = await this.createConflict(operation, serverResponse, policy.conflictResolution)
        result.conflicts.push(conflict)
      } else {
        result.errors.push(`Operation ${operation.id} failed: ${serverResponse?.error || 'Unknown error'}`)
      }
    }

    return result
  }

  /**
   * Process pull response from server
   */
  private async processPullResponse(
    batchId: string,
    response: any,
    policy: SyncPolicy
  ): Promise<DeltaSyncResult> {
    const result: DeltaSyncResult = {
      success: true,
      batchId,
      syncedOperations: 0,
      conflicts: [],
      nextSyncToken: response.nextSyncToken,
      errors: []
    }

    const incomingOperations = response.operations || []

    for (const remoteOp of incomingOperations) {
      try {
        // Check for local conflicts
        const localConflict = await this.detectLocalConflict(remoteOp)
        
        if (localConflict) {
          const conflict = await this.resolveConflict(localConflict, remoteOp, policy.conflictResolution)
          result.conflicts.push(conflict)
        } else {
          // Apply remote operation
          await this.applyRemoteOperation(remoteOp)
          result.syncedOperations++
        }
      } catch (error) {
        result.errors.push(`Failed to apply operation ${remoteOp.id}: ${error}`)
      }
    }

    return result
  }

  /**
   * Detect local conflict with incoming operation
   */
  private async detectLocalConflict(remoteOp: DeltaOperation): Promise<DeltaOperation | null> {
    const sql = `
      SELECT * FROM delta_operations 
      WHERE entity_id = ? AND entity_type = ? AND sync_status = 'pending'
      AND timestamp > ?
    `
    
    const result = await this.db.executeSql(sql, [
      remoteOp.entityId,
      remoteOp.entityType,
      remoteOp.timestamp
    ])
    
    if (result[0].rows.length > 0) {
      const row = result[0].rows.item(0)
      return {
        id: row.id,
        entityType: row.entity_type,
        entityId: row.entity_id,
        operationType: row.operation_type,
        fieldName: row.field_name,
        oldValue: row.old_value ? JSON.parse(row.old_value) : undefined,
        newValue: row.new_value ? JSON.parse(row.new_value) : undefined,
        rowVersion: row.row_version,
        timestamp: row.timestamp,
        userId: row.user_id,
        syncStatus: row.sync_status
      }
    }
    
    return null
  }

  /**
   * Resolve conflict between local and remote operations
   */
  private async resolveConflict(
    localOp: DeltaOperation,
    remoteOp: DeltaOperation,
    strategy: ConflictResolutionStrategy
  ): Promise<DeltaConflict> {
    const conflict: DeltaConflict = {
      id: `conflict_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      entityType: localOp.entityType,
      entityId: localOp.entityId,
      fieldName: localOp.fieldName,
      localOperation: localOp,
      remoteOperation: remoteOp,
      resolutionStrategy: strategy
    }

    switch (strategy) {
      case 'last_write_wins':
        const localTime = new Date(localOp.timestamp)
        const remoteTime = new Date(remoteOp.timestamp)
        
        if (remoteTime > localTime) {
          // Remote wins
          await this.applyRemoteOperation(remoteOp)
          await this.markOperationConflicted(localOp.id, conflict.id)
          conflict.resolvedValue = remoteOp.newValue
        } else {
          // Local wins - keep local change
          conflict.resolvedValue = localOp.newValue
        }
        break

      case 'operational_transform':
        conflict.resolvedValue = await this.performOperationalTransform(localOp, remoteOp)
        break

      case 'field_level_merge':
        conflict.resolvedValue = await this.performFieldLevelMerge(localOp, remoteOp)
        break

      case 'manual_resolution':
        // Store conflict for manual resolution
        await this.storeConflictForManualResolution(conflict)
        break
    }

    conflict.resolvedAt = new Date().toISOString()
    return conflict
  }

  /**
   * Perform operational transform
   */
  private async performOperationalTransform(
    localOp: DeltaOperation,
    remoteOp: DeltaOperation
  ): Promise<any> {
    // Simplified operational transform for demonstration
    // In production, this would implement proper OT algorithms
    
    if (localOp.operationType === 'update' && remoteOp.operationType === 'update') {
      if (localOp.fieldName === remoteOp.fieldName) {
        // Same field conflict - use last write wins as fallback
        const localTime = new Date(localOp.timestamp)
        const remoteTime = new Date(remoteOp.timestamp)
        return remoteTime > localTime ? remoteOp.newValue : localOp.newValue
      } else {
        // Different fields - merge both changes
        return {
          [localOp.fieldName!]: localOp.newValue,
          [remoteOp.fieldName!]: remoteOp.newValue
        }
      }
    }
    
    // Fallback to last write wins
    const localTime = new Date(localOp.timestamp)
    const remoteTime = new Date(remoteOp.timestamp)
    return remoteTime > localTime ? remoteOp.newValue : localOp.newValue
  }

  /**
   * Perform field-level merge
   */
  private async performFieldLevelMerge(
    localOp: DeltaOperation,
    remoteOp: DeltaOperation
  ): Promise<any> {
    // Get current entity state
    const currentEntity = await this.getEntityById(localOp.entityType, localOp.entityId)
    
    if (!currentEntity) {
      return remoteOp.newValue
    }

    // Merge field-by-field
    const merged = { ...currentEntity }
    
    if (localOp.fieldName && localOp.newValue !== undefined) {
      merged[localOp.fieldName] = localOp.newValue
    }
    
    if (remoteOp.fieldName && remoteOp.newValue !== undefined) {
      merged[remoteOp.fieldName] = remoteOp.newValue
    }
    
    return merged
  }

  /**
   * Apply remote operation to local database
   */
  private async applyRemoteOperation(remoteOp: DeltaOperation): Promise<void> {
    const tableName = this.getTableName(remoteOp.entityType)
    
    switch (remoteOp.operationType) {
      case 'create':
        if (remoteOp.newValue) {
          await this.insertEntity(tableName, remoteOp.newValue, remoteOp.rowVersion)
        }
        break
        
      case 'update':
        if (remoteOp.fieldName && remoteOp.newValue !== undefined) {
          await this.updateEntityField(tableName, remoteOp.entityId, remoteOp.fieldName, remoteOp.newValue, remoteOp.rowVersion)
        }
        break
        
      case 'delete':
        await this.deleteEntity(tableName, remoteOp.entityId)
        break
    }
  }

  /**
   * Create sync batch record
   */
  private async createSyncBatch(batchId: string, type: 'pull' | 'push', batchSize: number): Promise<void> {
    const sql = `
      INSERT INTO sync_batches (id, type, total_operations, started_at)
      VALUES (?, ?, ?, ?)
    `
    
    await this.db.executeSql(sql, [
      batchId,
      type,
      batchSize,
      new Date().toISOString()
    ])
  }

  /**
   * Update sync batch status
   */
  private async updateSyncBatchStatus(
    batchId: string,
    status: string,
    successful: number,
    failed: number,
    error?: string
  ): Promise<void> {
    const sql = `
      UPDATE sync_batches 
      SET status = ?, successful_operations = ?, failed_operations = ?, 
          completed_at = ?, error_message = ?
      WHERE id = ?
    `
    
    await this.db.executeSql(sql, [
      status,
      successful,
      failed,
      new Date().toISOString(),
      error || null,
      batchId
    ])
  }

  /**
   * Mark operation as synced
   */
  private async markOperationSynced(operationId: string, serverVersion?: number): Promise<void> {
    const sql = `
      UPDATE delta_operations 
      SET sync_status = 'synced'
      WHERE id = ?
    `
    
    await this.db.executeSql(sql, [operationId])
  }

  /**
   * Mark operation as conflicted
   */
  private async markOperationConflicted(operationId: string, conflictId: string): Promise<void> {
    const sql = `
      UPDATE delta_operations 
      SET sync_status = 'conflicted'
      WHERE id = ?
    `
    
    await this.db.executeSql(sql, [operationId])
  }

  /**
   * Get/Set sync tokens for incremental sync
   */
  private async getLastSyncToken(): Promise<string | undefined> {
    return await AsyncStorage.getItem('last_delta_sync_token') || undefined
  }

  private async saveLastSyncToken(token: string): Promise<void> {
    await AsyncStorage.setItem('last_delta_sync_token', token)
  }

  /**
   * Utility methods for entity operations
   */
  private async getEntityById(entityType: string, entityId: string): Promise<any | null> {
    const tableName = this.getTableName(entityType)
    const sql = `SELECT * FROM ${tableName} WHERE id = ?`
    
    const result = await this.db.executeSql(sql, [entityId])
    
    if (result[0].rows.length > 0) {
      return result[0].rows.item(0)
    }
    
    return null
  }

  private async insertEntity(tableName: string, entity: any, rowVersion: number): Promise<void> {
    // Implementation would depend on specific entity structure
    // This is a simplified version
  }

  private async updateEntityField(
    tableName: string,
    entityId: string,
    fieldName: string,
    value: any,
    rowVersion: number
  ): Promise<void> {
    const sql = `
      UPDATE ${tableName} 
      SET ${fieldName} = ?, row_version = ?, updated_at = ?
      WHERE id = ?
    `
    
    await this.db.executeSql(sql, [
      typeof value === 'object' ? JSON.stringify(value) : value,
      rowVersion,
      new Date().toISOString(),
      entityId
    ])
  }

  private async deleteEntity(tableName: string, entityId: string): Promise<void> {
    const sql = `DELETE FROM ${tableName} WHERE id = ?`
    await this.db.executeSql(sql, [entityId])
  }

  private async createConflict(
    operation: DeltaOperation,
    serverResponse: any,
    strategy: ConflictResolutionStrategy
  ): Promise<DeltaConflict> {
    // Implementation for creating conflict records
    return {
      id: `conflict_${Date.now()}`,
      entityType: operation.entityType,
      entityId: operation.entityId,
      fieldName: operation.fieldName,
      localOperation: operation,
      remoteOperation: serverResponse.conflictingOperation,
      resolutionStrategy: strategy
    }
  }

  private async storeConflictForManualResolution(conflict: DeltaConflict): Promise<void> {
    // Store conflict in sync_conflicts table for manual resolution
    const sql = `
      INSERT INTO sync_conflicts (
        id, entity_type, entity_id, field, local_value, remote_value,
        local_timestamp, remote_timestamp
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `
    
    await this.db.executeSql(sql, [
      conflict.id,
      conflict.entityType,
      conflict.entityId,
      conflict.fieldName || 'full_entity',
      JSON.stringify(conflict.localOperation.newValue),
      JSON.stringify(conflict.remoteOperation.newValue),
      conflict.localOperation.timestamp,
      conflict.remoteOperation.timestamp
    ])
  }

  /**
   * Exponential backoff retry logic
   */
  public async syncWithRetry(
    operation: () => Promise<DeltaSyncResult>,
    policy?: Partial<SyncPolicy>
  ): Promise<DeltaSyncResult> {
    const syncPolicy = { ...this.defaultPolicy, ...policy }
    let retryCount = 0
    let delay = syncPolicy.retryDelayMs

    while (retryCount < syncPolicy.maxRetries) {
      try {
        return await operation()
      } catch (error) {
        retryCount++
        
        if (retryCount >= syncPolicy.maxRetries) {
          throw error
        }

        // Exponential backoff with jitter
        const jitter = Math.random() * 0.1 * delay
        const backoffDelay = Math.min(
          delay * syncPolicy.backoffMultiplier + jitter,
          syncPolicy.maxRetryDelayMs
        )

        await new Promise(resolve => setTimeout(resolve, backoffDelay))
        delay = backoffDelay
      }
    }

    throw new Error('Max retries exceeded')
  }

  /**
   * Full bidirectional sync (pull then push)
   */
  public async fullSync(policy?: Partial<SyncPolicy>): Promise<{
    pullResult: DeltaSyncResult
    pushResult: DeltaSyncResult
  }> {
    // Pull changes first
    const pullResult = await this.syncWithRetry(
      () => this.pullChanges(policy),
      policy
    )

    // Then push local changes
    const pushResult = await this.syncWithRetry(
      () => this.pushChanges(policy),
      policy
    )

    return { pullResult, pushResult }
  }
}