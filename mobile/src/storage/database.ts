/**
 * SQLite Database Manager
 * Offline-first data storage with sync capabilities
 */

import SQLite, { SQLiteDatabase } from 'react-native-sqlite-storage'
import { 
  Gate, 
  Inspection, 
  ChecklistTemplate, 
  InspectionPhoto, 
  SyncConflict,
  QueueItem,
  User 
} from '../types'

// Enable debugging
SQLite.DEBUG(true)
SQLite.enablePromise(true)

export class DatabaseManager {
  private static instance: DatabaseManager
  private db: SQLiteDatabase | null = null
  private readonly DB_NAME = 'garagereg.db'
  private readonly DB_VERSION = '1.0'
  private readonly DB_DISPLAY_NAME = 'GarageReg Mobile Database'
  private readonly DB_SIZE = 200000

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager()
    }
    return DatabaseManager.instance
  }

  /**
   * Initialize database connection and create tables
   */
  public async initialize(): Promise<void> {
    try {
      this.db = await SQLite.openDatabase(
        this.DB_NAME,
        this.DB_VERSION,
        this.DB_DISPLAY_NAME,
        this.DB_SIZE
      )

      console.log('📱 SQLite database opened successfully')
      
      await this.createTables()
      await this.createIndexes()
      
      console.log('📱 Database initialized successfully')
    } catch (error) {
      console.error('❌ Database initialization failed:', error)
      throw error
    }
  }

  /**
   * Create all required tables
   */
  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized')

    const tables = [
      // Users table
      `CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        full_name TEXT,
        roles TEXT, -- JSON
        permissions TEXT, -- JSON
        last_login TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`,

      // Gates table
      `CREATE TABLE IF NOT EXISTS gates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gate_code TEXT UNIQUE,
        location TEXT,
        building_id TEXT,
        building_name TEXT,
        site_id TEXT,
        site_name TEXT,
        client_id TEXT,
        client_name TEXT,
        gate_type TEXT,
        status TEXT,
        manufacturer TEXT,
        model TEXT,
        serial_number TEXT,
        installation_date TEXT,
        last_maintenance TEXT,
        next_maintenance TEXT,
        qr_code TEXT,
        coordinates TEXT, -- JSON
        metadata TEXT, -- JSON
        sync_status TEXT DEFAULT 'synced',
        last_sync_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        -- Delta sync versioning fields
        row_version INTEGER DEFAULT 1,
        etag TEXT,
        local_changes TEXT, -- JSON array of changes since last sync
        server_version INTEGER DEFAULT 0,
        conflict_resolution_strategy TEXT DEFAULT 'last_write_wins'
      )`,

      // Checklist Templates table
      `CREATE TABLE IF NOT EXISTS checklist_templates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        version TEXT,
        items TEXT, -- JSON
        estimated_duration INTEGER,
        is_active BOOLEAN DEFAULT 1,
        sync_status TEXT DEFAULT 'synced',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`,

      // Inspections table
      `CREATE TABLE IF NOT EXISTS inspections (
        id TEXT PRIMARY KEY,
        gate_id TEXT NOT NULL,
        template_id TEXT NOT NULL,
        template_name TEXT,
        inspector_id TEXT NOT NULL,
        inspector_name TEXT,
        status TEXT DEFAULT 'scheduled',
        priority TEXT DEFAULT 'normal',
        scheduled_date TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        estimated_duration INTEGER,
        actual_duration INTEGER,
        location TEXT,
        weather TEXT,
        notes TEXT,
        checklist TEXT, -- JSON
        signature TEXT,
        sync_status TEXT DEFAULT 'pending',
        last_sync_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        -- Delta sync versioning fields
        row_version INTEGER DEFAULT 1,
        etag TEXT,
        local_changes TEXT, -- JSON array of changes since last sync
        server_version INTEGER DEFAULT 0,
        conflict_resolution_strategy TEXT DEFAULT 'last_write_wins',
        FOREIGN KEY (gate_id) REFERENCES gates (id),
        FOREIGN KEY (template_id) REFERENCES checklist_templates (id)
      )`,

      // Photos table
      `CREATE TABLE IF NOT EXISTS inspection_photos (
        id TEXT PRIMARY KEY,
        inspection_id TEXT NOT NULL,
        checklist_item_id TEXT,
        uri TEXT NOT NULL,
        remote_uri TEXT,
        file_name TEXT NOT NULL,
        size INTEGER,
        mime_type TEXT,
        timestamp TEXT NOT NULL,
        location TEXT, -- JSON
        upload_status TEXT DEFAULT 'pending',
        attempts INTEGER DEFAULT 0,
        last_attempt_at TEXT,
        error_message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inspection_id) REFERENCES inspections (id)
      )`,

      // Sync Conflicts table
      `CREATE TABLE IF NOT EXISTS sync_conflicts (
        id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        field TEXT NOT NULL,
        local_value TEXT,
        remote_value TEXT,
        local_timestamp TEXT,
        remote_timestamp TEXT,
        resolution TEXT,
        resolved_at TEXT,
        resolved_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`,

      // Sync Queue table
      `CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        data TEXT, -- JSON
        priority INTEGER DEFAULT 1,
        attempts INTEGER DEFAULT 0,
        max_attempts INTEGER DEFAULT 3,
        scheduled_at TEXT NOT NULL,
        last_attempt_at TEXT,
        error_message TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`,

      // App Settings table
      `CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`,

      // Delta Sync Operations table
      `CREATE TABLE IF NOT EXISTS delta_operations (
        id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        operation_type TEXT NOT NULL, -- create, update, delete
        field_name TEXT,
        old_value TEXT,
        new_value TEXT,
        row_version INTEGER,
        timestamp TEXT NOT NULL,
        user_id TEXT,
        sync_status TEXT DEFAULT 'pending', -- pending, synced, conflicted
        batch_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`,

      // Sync Batches table for batch operations
      `CREATE TABLE IF NOT EXISTS sync_batches (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL, -- pull, push
        status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
        started_at TEXT,
        completed_at TEXT,
        total_operations INTEGER DEFAULT 0,
        successful_operations INTEGER DEFAULT 0,
        failed_operations INTEGER DEFAULT 0,
        last_sync_token TEXT,
        next_sync_token TEXT,
        retry_count INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`
    ]

    for (const sql of tables) {
      await this.db.executeSql(sql)
    }
  }

  /**
   * Create database indexes for performance
   */
  private async createIndexes(): Promise<void> {
    if (!this.db) return

    const indexes = [
      'CREATE INDEX IF NOT EXISTS idx_gates_qr_code ON gates (qr_code)',
      'CREATE INDEX IF NOT EXISTS idx_gates_building_id ON gates (building_id)',
      'CREATE INDEX IF NOT EXISTS idx_gates_sync_status ON gates (sync_status)',
      'CREATE INDEX IF NOT EXISTS idx_inspections_gate_id ON inspections (gate_id)',
      'CREATE INDEX IF NOT EXISTS idx_inspections_status ON inspections (status)',
      'CREATE INDEX IF NOT EXISTS idx_inspections_scheduled_date ON inspections (scheduled_date)',
      'CREATE INDEX IF NOT EXISTS idx_inspections_sync_status ON inspections (sync_status)',
      'CREATE INDEX IF NOT EXISTS idx_photos_inspection_id ON inspection_photos (inspection_id)',
      'CREATE INDEX IF NOT EXISTS idx_photos_upload_status ON inspection_photos (upload_status)',
      'CREATE INDEX IF NOT EXISTS idx_queue_status ON sync_queue (status)',
      'CREATE INDEX IF NOT EXISTS idx_queue_scheduled_at ON sync_queue (scheduled_at)'
    ]

    for (const sql of indexes) {
      await this.db.executeSql(sql)
    }
  }

  /**
   * Execute raw SQL query
   */
  public async executeSql(sql: string, params: any[] = []): Promise<any> {
    if (!this.db) throw new Error('Database not initialized')
    
    try {
      const result = await this.db.executeSql(sql, params)
      return result
    } catch (error) {
      console.error('❌ SQL execution failed:', sql, error)
      throw error
    }
  }

  /**
   * Close database connection
   */
  public async close(): Promise<void> {
    if (this.db) {
      await this.db.close()
      this.db = null
      console.log('📱 Database connection closed')
    }
  }

  /**
   * Clear all data (for testing or logout)
   */
  public async clearAllData(): Promise<void> {
    if (!this.db) return

    const tables = [
      'users', 
      'gates', 
      'checklist_templates', 
      'inspections', 
      'inspection_photos',
      'sync_conflicts', 
      'sync_queue', 
      'app_settings'
    ]

    for (const table of tables) {
      await this.db.executeSql(`DELETE FROM ${table}`)
    }

    console.log('📱 All data cleared from database')
  }

  /**
   * Get database statistics
   */
  public async getStats(): Promise<Record<string, number>> {
    if (!this.db) return {}

    const stats: Record<string, number> = {}
    
    const tables = [
      'gates', 
      'checklist_templates', 
      'inspections', 
      'inspection_photos',
      'sync_conflicts', 
      'sync_queue'
    ]

    for (const table of tables) {
      const result = await this.db.executeSql(`SELECT COUNT(*) as count FROM ${table}`)
      stats[table] = result[0].rows.item(0).count
    }

    return stats
  }

  /**
   * Backup database to JSON
   */
  public async exportData(): Promise<string> {
    if (!this.db) throw new Error('Database not initialized')

    const data: Record<string, any[]> = {}
    
    const tables = [
      'gates', 
      'checklist_templates', 
      'inspections', 
      'inspection_photos'
    ]

    for (const table of tables) {
      const result = await this.db.executeSql(`SELECT * FROM ${table}`)
      const rows = []
      
      for (let i = 0; i < result[0].rows.length; i++) {
        rows.push(result[0].rows.item(i))
      }
      
      data[table] = rows
    }

    return JSON.stringify(data, null, 2)
  }

  /**
   * Check if database is ready
   */
  public isReady(): boolean {
    return this.db !== null
  }
}

export default DatabaseManager.getInstance()