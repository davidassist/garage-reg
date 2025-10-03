/**
 * Conflict Resolver - Handles data synchronization conflicts
 * Provides resolution strategies and UI for manual resolution
 */

import { 
  SyncConflict, 
  ConflictResolution, 
  Gate, 
  Inspection 
} from '../types'
import { DatabaseManager } from '../storage/database'

export interface ConflictResolutionStrategy {
  type: ConflictResolution
  description: string
  apply: (conflict: SyncConflict) => any
}

export class ConflictResolver {
  private db = DatabaseManager.getInstance()

  /**
   * Get all unresolved conflicts
   */
  public async getUnresolvedConflicts(): Promise<SyncConflict[]> {
    const sql = `
      SELECT * FROM sync_conflicts 
      WHERE resolution IS NULL 
      ORDER BY created_at DESC
    `
    
    const result = await this.db.executeSql(sql, [])
    
    const conflicts: SyncConflict[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      const row = result[0].rows.item(i)
      conflicts.push({
        id: row.id,
        entityType: row.entity_type,
        entityId: row.entity_id,
        field: row.field,
        localValue: JSON.parse(row.local_value),
        remoteValue: JSON.parse(row.remote_value),
        localTimestamp: row.local_timestamp,
        remoteTimestamp: row.remote_timestamp,
        resolution: row.resolution,
        resolvedAt: row.resolved_at,
        resolvedBy: row.resolved_by
      })
    }
    
    return conflicts
  }

  /**
   * Get available resolution strategies for a conflict
   */
  public getResolutionStrategies(conflict: SyncConflict): ConflictResolutionStrategy[] {
    const strategies: ConflictResolutionStrategy[] = [
      {
        type: 'use_local',
        description: 'Keep local changes (overwrite server)',
        apply: (conflict) => conflict.localValue
      },
      {
        type: 'use_remote',
        description: 'Accept server changes (discard local)',
        apply: (conflict) => conflict.remoteValue
      }
    ]

    // Add merge strategy if applicable
    if (this.isMergeable(conflict)) {
      strategies.push({
        type: 'merge',
        description: 'Merge both versions intelligently',
        apply: (conflict) => this.performMerge(conflict)
      })
    }

    return strategies
  }

  /**
   * Check if conflict can be automatically merged
   */
  private isMergeable(conflict: SyncConflict): boolean {
    // Only certain entity types and fields can be merged
    if (conflict.entityType === 'gate') {
      // Gate metadata can be merged
      return conflict.field === 'metadata'
    }
    
    if (conflict.entityType === 'inspection') {
      // Notes can be appended, checklist responses can be merged if non-conflicting
      return ['notes', 'checklistResponses'].includes(conflict.field)
    }

    return false
  }

  /**
   * Perform intelligent merge of conflicting values
   */
  private performMerge(conflict: SyncConflict): any {
    const local = conflict.localValue
    const remote = conflict.remoteValue

    switch (conflict.entityType) {
      case 'gate':
        return this.mergeGateData(local, remote, conflict.field)
      
      case 'inspection':
        return this.mergeInspectionData(local, remote, conflict.field)
      
      default:
        // Fallback to local value if merge not implemented
        return local
    }
  }

  /**
   * Merge gate data fields
   */
  private mergeGateData(local: any, remote: any, field: string): any {
    if (field === 'metadata') {
      // Merge metadata objects, remote takes precedence on conflicts
      return { ...local, ...remote }
    }
    
    return local
  }

  /**
   * Merge inspection data fields
   */
  private mergeInspectionData(local: any, remote: any, field: string): any {
    if (field === 'notes') {
      // Append both notes with separator
      const localNotes = local || ''
      const remoteNotes = remote || ''
      
      if (!localNotes && !remoteNotes) return ''
      if (!localNotes) return remoteNotes
      if (!remoteNotes) return localNotes
      
      return `${localNotes}\n\n--- Remote changes ---\n${remoteNotes}`
    }
    
    if (field === 'checklistResponses') {
      // Merge checklist responses, keeping both if they don't conflict
      const merged = { ...local }
      
      for (const [key, value] of Object.entries(remote)) {
        if (!merged[key] || merged[key] === value) {
          merged[key] = value
        } else {
          // Conflict in same checklist item - keep local by default
          // Could be enhanced to show both options
        }
      }
      
      return merged
    }
    
    return local
  }

  /**
   * Resolve conflict with chosen strategy
   */
  public async resolveConflict(
    conflictId: string,
    resolution: ConflictResolution,
    resolvedBy: string
  ): Promise<void> {
    const conflicts = await this.getUnresolvedConflicts()
    const conflict = conflicts.find(c => c.id === conflictId)
    
    if (!conflict) {
      throw new Error('Conflict not found')
    }

    // Get resolution strategy and apply it
    const strategies = this.getResolutionStrategies(conflict)
    const strategy = strategies.find(s => s.type === resolution)
    
    if (!strategy) {
      throw new Error(`Resolution strategy '${resolution}' not available`)
    }

    const resolvedValue = strategy.apply(conflict)
    
    // Apply resolution to the main data
    await this.applyResolution(conflict, resolvedValue)
    
    // Mark conflict as resolved
    await this.markConflictResolved(conflictId, resolution, resolvedBy)
  }

  /**
   * Apply resolved value to the main entity
   */
  private async applyResolution(conflict: SyncConflict, resolvedValue: any): Promise<void> {
    let query = ''
    let params: any[] = []
    
    switch (conflict.entityType) {
      case 'gate':
        if (conflict.field === 'metadata') {
          query = `UPDATE gates 
                  SET metadata = ?, sync_status = 'synced', last_sync_at = ?
                  WHERE id = ?`
          params = [JSON.stringify(resolvedValue), new Date().toISOString(), conflict.entityId]
        } else {
          // Handle other gate fields
          query = `UPDATE gates 
                  SET ${conflict.field} = ?, sync_status = 'synced', last_sync_at = ?
                  WHERE id = ?`
          params = [resolvedValue, new Date().toISOString(), conflict.entityId]
        }
        break
        
      case 'inspection':
        if (conflict.field === 'checklistResponses') {
          query = `UPDATE inspections 
                  SET checklist_responses = ?, sync_status = 'synced', last_sync_at = ?
                  WHERE id = ?`
          params = [JSON.stringify(resolvedValue), new Date().toISOString(), conflict.entityId]
        } else {
          query = `UPDATE inspections 
                  SET ${conflict.field} = ?, sync_status = 'synced', last_sync_at = ?
                  WHERE id = ?`
          params = [resolvedValue, new Date().toISOString(), conflict.entityId]
        }
        break
        
      default:
        throw new Error(`Unknown entity type: ${conflict.entityType}`)
    }
    
    await this.db.executeSql(query, params)
  }

  /**
   * Mark conflict as resolved in database
   */
  private async markConflictResolved(
    conflictId: string,
    resolution: ConflictResolution,
    resolvedBy: string
  ): Promise<void> {
    const sql = `
      UPDATE sync_conflicts 
      SET resolution = ?, resolved_at = ?, resolved_by = ?
      WHERE id = ?
    `
    
    await this.db.executeSql(sql, [
      resolution, 
      new Date().toISOString(), 
      resolvedBy, 
      conflictId
    ])
  }

  /**
   * Auto-resolve conflicts where possible
   */
  public async autoResolveConflicts(): Promise<{
    resolved: number
    remaining: number
  }> {
    const conflicts = await this.getUnresolvedConflicts()
    let resolvedCount = 0
    
    for (const conflict of conflicts) {
      const autoResolution = this.getAutoResolution(conflict)
      
      if (autoResolution) {
        try {
          await this.resolveConflict(conflict.id, autoResolution, 'system')
          resolvedCount++
        } catch (error) {
          // Continue with other conflicts if one fails
        }
      }
    }
    
    return {
      resolved: resolvedCount,
      remaining: conflicts.length - resolvedCount
    }
  }

  /**
   * Get automatic resolution strategy for conflict
   */
  private getAutoResolution(conflict: SyncConflict): ConflictResolution | null {
    const localTime = new Date(conflict.localTimestamp)
    const remoteTime = new Date(conflict.remoteTimestamp)
    
    // Simple timestamp-based resolution for some cases
    if (conflict.entityType === 'gate' && conflict.field === 'metadata') {
      // For metadata, we can auto-merge
      return 'merge'
    }
    
    // For most cases, prefer newer data
    if (remoteTime > localTime) {
      return 'use_remote'
    } else {
      return 'use_local'
    }
  }

  /**
   * Create new conflict record
   */
  public async createConflict(conflict: Omit<SyncConflict, 'id'>): Promise<string> {
    const conflictId = `conflict_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    const sql = `
      INSERT INTO sync_conflicts (
        id, entity_type, entity_id, field,
        local_value, remote_value,
        local_timestamp, remote_timestamp,
        created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `
    
    await this.db.executeSql(sql, [
      conflictId,
      conflict.entityType,
      conflict.entityId,
      conflict.field,
      JSON.stringify(conflict.localValue),
      JSON.stringify(conflict.remoteValue),
      conflict.localTimestamp,
      conflict.remoteTimestamp,
      new Date().toISOString()
    ])
    
    return conflictId
  }

  /**
   * Clear all resolved conflicts older than specified days
   */
  public async cleanupOldConflicts(olderThanDays = 30): Promise<number> {
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - olderThanDays)
    
    const sql = `
      DELETE FROM sync_conflicts 
      WHERE resolution IS NOT NULL 
      AND resolved_at < ?
    `
    
    const result = await this.db.executeSql(sql, [cutoffDate.toISOString()])
    return result[0].rowsAffected
  }
}