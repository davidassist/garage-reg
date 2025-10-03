/**
 * Gates Repository - SQLite operations for gates
 */

import DatabaseManager from './database'
import { Gate, SyncStatus } from '../types'

export class GatesRepository {
  private db = DatabaseManager

  /**
   * Get all gates from local storage
   */
  async getAll(): Promise<Gate[]> {
    const sql = `
      SELECT * FROM gates 
      ORDER BY building_name, name
    `
    const result = await this.db.executeSql(sql)
    
    const gates: Gate[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      gates.push(this.mapRowToGate(result[0].rows.item(i)))
    }
    
    return gates
  }

  /**
   * Get gate by ID
   */
  async getById(id: string): Promise<Gate | null> {
    const sql = `SELECT * FROM gates WHERE id = ?`
    const result = await this.db.executeSql(sql, [id])
    
    if (result[0].rows.length === 0) {
      return null
    }
    
    return this.mapRowToGate(result[0].rows.item(0))
  }

  /**
   * Get gate by QR code
   */
  async getByQRCode(qrCode: string): Promise<Gate | null> {
    const sql = `SELECT * FROM gates WHERE qr_code = ?`
    const result = await this.db.executeSql(sql, [qrCode])
    
    if (result[0].rows.length === 0) {
      return null
    }
    
    return this.mapRowToGate(result[0].rows.item(0))
  }

  /**
   * Search gates by building or site
   */
  async search(query: string): Promise<Gate[]> {
    const sql = `
      SELECT * FROM gates 
      WHERE name LIKE ? OR building_name LIKE ? OR site_name LIKE ?
      ORDER BY building_name, name
    `
    const searchTerm = `%${query}%`
    const result = await this.db.executeSql(sql, [searchTerm, searchTerm, searchTerm])
    
    const gates: Gate[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      gates.push(this.mapRowToGate(result[0].rows.item(i)))
    }
    
    return gates
  }

  /**
   * Insert or update gate
   */
  async upsert(gate: Gate): Promise<void> {
    const sql = `
      INSERT OR REPLACE INTO gates (
        id, name, gate_code, location, building_id, building_name,
        site_id, site_name, client_id, client_name, gate_type, status,
        manufacturer, model, serial_number, installation_date,
        last_maintenance, next_maintenance, qr_code, coordinates,
        metadata, sync_status, last_sync_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `
    
    await this.db.executeSql(sql, [
      gate.id,
      gate.name,
      gate.gateCode,
      gate.location,
      gate.buildingId,
      gate.buildingName,
      gate.siteId,
      gate.siteName,
      gate.clientId,
      gate.clientName,
      gate.gateType,
      gate.status,
      gate.manufacturer,
      gate.model,
      gate.serialNumber,
      gate.installationDate,
      gate.lastMaintenance,
      gate.nextMaintenance,
      gate.qrCode,
      JSON.stringify(gate.coordinates),
      JSON.stringify(gate.metadata),
      gate.syncStatus,
      gate.lastSyncAt,
      new Date().toISOString()
    ])
  }

  /**
   * Bulk upsert gates (for sync)
   */
  async bulkUpsert(gates: Gate[]): Promise<void> {
    for (const gate of gates) {
      await this.upsert({ ...gate, syncStatus: 'synced' })
    }
  }

  /**
   * Update sync status
   */
  async updateSyncStatus(id: string, status: SyncStatus, lastSyncAt?: string): Promise<void> {
    const sql = `
      UPDATE gates 
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
   * Get gates with pending sync
   */
  async getPendingSync(): Promise<Gate[]> {
    const sql = `
      SELECT * FROM gates 
      WHERE sync_status IN ('pending', 'error')
      ORDER BY updated_at
    `
    const result = await this.db.executeSql(sql)
    
    const gates: Gate[] = []
    for (let i = 0; i < result[0].rows.length; i++) {
      gates.push(this.mapRowToGate(result[0].rows.item(i)))
    }
    
    return gates
  }

  /**
   * Delete gate
   */
  async delete(id: string): Promise<void> {
    const sql = `DELETE FROM gates WHERE id = ?`
    await this.db.executeSql(sql, [id])
  }

  /**
   * Get count by status
   */
  async getCountByStatus(): Promise<Record<string, number>> {
    const sql = `
      SELECT status, COUNT(*) as count 
      FROM gates 
      GROUP BY status
    `
    const result = await this.db.executeSql(sql)
    
    const counts: Record<string, number> = {}
    for (let i = 0; i < result[0].rows.length; i++) {
      const row = result[0].rows.item(i)
      counts[row.status] = row.count
    }
    
    return counts
  }

  /**
   * Check if gate exists locally
   */
  async exists(id: string): Promise<boolean> {
    const sql = `SELECT 1 FROM gates WHERE id = ? LIMIT 1`
    const result = await this.db.executeSql(sql, [id])
    return result[0].rows.length > 0
  }

  /**
   * Map database row to Gate object
   */
  private mapRowToGate(row: any): Gate {
    return {
      id: row.id,
      name: row.name,
      gateCode: row.gate_code,
      location: row.location,
      buildingId: row.building_id,
      buildingName: row.building_name,
      siteId: row.site_id,
      siteName: row.site_name,
      clientId: row.client_id,
      clientName: row.client_name,
      gateType: row.gate_type,
      status: row.status,
      manufacturer: row.manufacturer,
      model: row.model,
      serialNumber: row.serial_number,
      installationDate: row.installation_date,
      lastMaintenance: row.last_maintenance,
      nextMaintenance: row.next_maintenance,
      qrCode: row.qr_code,
      coordinates: row.coordinates ? JSON.parse(row.coordinates) : undefined,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
      syncStatus: row.sync_status,
      lastSyncAt: row.last_sync_at
    }
  }
}