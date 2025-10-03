/**
 * Inspections Repository - SQLite operations for inspections
 */

import DatabaseManager from './database'
import { Inspection, InspectionStatus, SyncStatus } from '../types'

export class InspectionsRepository {
  private db = DatabaseManager

  /**
   * Get all inspections
   */
  async getAll(): Promise<Inspection[]> {
    const sql = `
      SELECT * FROM inspections 
      ORDER BY scheduled_date DESC
    `
    const result = await this.db.executeSql(sql)
    
    const inspections: Inspection[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      inspections.push(this.mapRowToInspection(result[0].rows.item(i)))
    }
    
    return inspections
  }

  /**
   * Get inspection by ID
   */
  async getById(id: string): Promise<Inspection | null> {
    const sql = `SELECT * FROM inspections WHERE id = ?`
    const result = await this.db.executeSql(sql, [id])
    
    if (result[0].rows.length === 0) {
      return null
    }
    
    return this.mapRowToInspection(result[0].rows.item(0))
  }

  /**
   * Get inspections by status
   */
  async getByStatus(status: InspectionStatus): Promise<Inspection[]> {
    const sql = `
      SELECT * FROM inspections 
      WHERE status = ?
      ORDER BY scheduled_date ASC
    `
    const result = await this.db.executeSql(sql, [status])
    
    const inspections: Inspection[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      inspections.push(this.mapRowToInspection(result[0].rows.item(i)))
    }
    
    return inspections
  }

  /**
   * Get inspections by gate
   */
  async getByGateId(gateId: string): Promise<Inspection[]> {
    const sql = `
      SELECT * FROM inspections 
      WHERE gate_id = ?
      ORDER BY scheduled_date DESC
    `
    const result = await this.db.executeSql(sql, [gateId])
    
    const inspections: Inspection[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      inspections.push(this.mapRowToInspection(result[0].rows.item(i)))
    }
    
    return inspections
  }

  /**
   * Get active (in progress) inspections
   */
  async getActive(): Promise<Inspection[]> {
    return this.getByStatus('in_progress')
  }

  /**
   * Get scheduled inspections for today
   */
  async getTodaysScheduled(): Promise<Inspection[]> {
    const today = new Date().toISOString().split('T')[0]
    const sql = `
      SELECT * FROM inspections 
      WHERE DATE(scheduled_date) = ? AND status = 'scheduled'
      ORDER BY scheduled_date ASC
    `
    const result = await this.db.executeSql(sql, [today])
    
    const inspections: Inspection[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      inspections.push(this.mapRowToInspection(result[0].rows.item(i)))
    }
    
    return inspections
  }

  /**
   * Get overdue inspections
   */
  async getOverdue(): Promise<Inspection[]> {
    const now = new Date().toISOString()
    const sql = `
      SELECT * FROM inspections 
      WHERE scheduled_date < ? AND status = 'scheduled'
      ORDER BY scheduled_date ASC
    `
    const result = await this.db.executeSql(sql, [now])
    
    const inspections: Inspection[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      inspections.push(this.mapRowToInspection(result[0].rows.item(i)))
    }
    
    return inspections
  }

  /**
   * Create new inspection
   */
  async create(inspection: Omit<Inspection, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
    const id = `insp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const now = new Date().toISOString()
    
    const sql = `
      INSERT INTO inspections (
        id, gate_id, template_id, template_name, inspector_id, inspector_name,
        status, priority, scheduled_date, started_at, completed_at,
        estimated_duration, actual_duration, location, weather, notes,
        checklist, signature, sync_status, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `
    
    await this.db.executeSql(sql, [
      id,
      inspection.gateId,
      inspection.templateId,
      inspection.templateName,
      inspection.inspectorId,
      inspection.inspectorName,
      inspection.status,
      inspection.priority,
      inspection.scheduledDate,
      inspection.startedAt,
      inspection.completedAt,
      inspection.estimatedDuration,
      inspection.actualDuration,
      inspection.location,
      inspection.weather,
      inspection.notes,
      JSON.stringify(inspection.checklist),
      inspection.signature,
      inspection.syncStatus || 'pending',
      now,
      now
    ])
    
    return id
  }

  /**
   * Update inspection
   */
  async update(id: string, updates: Partial<Inspection>): Promise<void> {
    const fields = []
    const values = []
    
    // Build dynamic update query
    for (const [key, value] of Object.entries(updates)) {
      const dbKey = key.replace(/([A-Z])/g, '_$1').toLowerCase()
      
      if (key === 'checklist' || key === 'photos') {
        fields.push(`${dbKey} = ?`)
        values.push(JSON.stringify(value))
      } else {
        fields.push(`${dbKey} = ?`)
        values.push(value)
      }
    }
    
    fields.push('updated_at = ?')
    values.push(new Date().toISOString())
    values.push(id)
    
    const sql = `UPDATE inspections SET ${fields.join(', ')} WHERE id = ?`
    await this.db.executeSql(sql, values)
  }

  /**
   * Start inspection (change status to in_progress)
   */
  async start(id: string): Promise<void> {
    const now = new Date().toISOString()
    await this.update(id, {
      status: 'in_progress',
      startedAt: now,
      syncStatus: 'pending'
    })
  }

  /**
   * Complete inspection
   */
  async complete(id: string, signature?: string): Promise<void> {
    const inspection = await this.getById(id)
    if (!inspection) throw new Error('Inspection not found')
    
    const completedAt = new Date().toISOString()
    const actualDuration = inspection.startedAt 
      ? Math.round((new Date(completedAt).getTime() - new Date(inspection.startedAt).getTime()) / 60000)
      : undefined
    
    await this.update(id, {
      status: 'completed',
      completedAt,
      actualDuration,
      signature,
      syncStatus: 'pending'
    })
  }

  /**
   * Get inspections with pending sync
   */
  async getPendingSync(): Promise<Inspection[]> {
    const sql = `
      SELECT * FROM inspections 
      WHERE sync_status IN ('pending', 'error')
      ORDER BY updated_at
    `
    const result = await this.db.executeSql(sql)
    
    const inspections: Inspection[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      inspections.push(this.mapRowToInspection(result[0].rows.item(i)))
    }
    
    return inspections
  }

  /**
   * Update sync status
   */
  async updateSyncStatus(id: string, status: SyncStatus, lastSyncAt?: string): Promise<void> {
    const sql = `
      UPDATE inspections 
      SET sync_status = ?, last_sync_at = ?, updated_at = ?
      WHERE id = ?
    `
    await this.db.executeSql(sql, [
      status,
      lastSyncAt || new Date().toISOString(),
      new Date().toISOString(),
      id
    ])
  }

  /**
   * Delete inspection
   */
  async delete(id: string): Promise<void> {
    // Also delete related photos
    await this.db.executeSql('DELETE FROM inspection_photos WHERE inspection_id = ?', [id])
    await this.db.executeSql('DELETE FROM inspections WHERE id = ?', [id])
  }

  /**
   * Get inspection statistics
   */
  async getStats(): Promise<Record<string, number>> {
    const sql = `
      SELECT 
        status,
        COUNT(*) as count
      FROM inspections 
      GROUP BY status
    `
    const result = await this.db.executeSql(sql)
    
    const stats: Record<string, number> = {}
    for (let i = 0; i < result[0].rows.length; i++) {
      const row = result[0].rows.item(i)
      stats[row.status] = row.count
    }
    
    return stats
  }

  /**
   * Map database row to Inspection object
   */
  private mapRowToInspection(row: any): Inspection {
    return {
      id: row.id,
      gateId: row.gate_id,
      templateId: row.template_id,
      templateName: row.template_name,
      inspectorId: row.inspector_id,
      inspectorName: row.inspector_name,
      status: row.status,
      priority: row.priority,
      scheduledDate: row.scheduled_date,
      startedAt: row.started_at,
      completedAt: row.completed_at,
      estimatedDuration: row.estimated_duration,
      actualDuration: row.actual_duration,
      location: row.location,
      weather: row.weather,
      notes: row.notes,
      photos: [], // Photos loaded separately
      checklist: row.checklist ? JSON.parse(row.checklist) : [],
      signature: row.signature,
      syncStatus: row.sync_status,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      lastSyncAt: row.last_sync_at
    }
  }
}