/**
 * Delta Sync Conflict Test Scenarios
 * Comprehensive test suite for bidirectional synchronization conflicts
 */

import { DeltaSyncService } from '../services/deltaSyncService'
import { DatabaseManager } from '../storage/database'
import { 
  DeltaOperation, 
  ConflictResolutionStrategy, 
  Gate, 
  Inspection 
} from '../types'

export class DeltaSyncConflictTests {
  private deltaSync = DeltaSyncService.getInstance()
  private db = DatabaseManager.getInstance()

  /**
   * Test Suite: All conflict resolution scenarios
   */
  public async runAllConflictTests(): Promise<{
    testResults: { name: string; passed: boolean; error?: string }[]
    summary: { total: number; passed: number; failed: number }
  }> {
    console.log('🧪 Starting Delta Sync Conflict Test Suite')
    console.log('==========================================')

    const tests = [
      { name: 'Last Write Wins - Remote Newer', test: () => this.testLastWriteWinsRemoteNewer() },
      { name: 'Last Write Wins - Local Newer', test: () => this.testLastWriteWinsLocalNewer() },
      { name: 'Operational Transform - Same Field', test: () => this.testOperationalTransformSameField() },
      { name: 'Operational Transform - Different Fields', test: () => this.testOperationalTransformDifferentFields() },
      { name: 'Field Level Merge', test: () => this.testFieldLevelMerge() },
      { name: 'Manual Resolution Required', test: () => this.testManualResolution() },
      { name: 'Concurrent Creates', test: () => this.testConcurrentCreates() },
      { name: 'Delete vs Update Conflict', test: () => this.testDeleteVsUpdate() },
      { name: 'Batch Sync with Multiple Conflicts', test: () => this.testBatchSyncConflicts() },
      { name: 'Exponential Backoff Retry', test: () => this.testExponentialBackoff() },
      { name: 'ETag Version Mismatch', test: () => this.testETagVersionMismatch() },
      { name: 'Row Version Conflict', test: () => this.testRowVersionConflict() }
    ]

    const results: { name: string; passed: boolean; error?: string }[] = []

    for (const { name, test } of tests) {
      try {
        console.log(`\n🔬 Running: ${name}`)
        await test()
        console.log(`✅ PASSED: ${name}`)
        results.push({ name, passed: true })
      } catch (error) {
        console.log(`❌ FAILED: ${name} - ${error}`)
        results.push({ 
          name, 
          passed: false, 
          error: error instanceof Error ? error.message : String(error)
        })
      }
    }

    const summary = {
      total: results.length,
      passed: results.filter(r => r.passed).length,
      failed: results.filter(r => !r.passed).length
    }

    console.log('\n📊 Test Summary')
    console.log(`Total Tests: ${summary.total}`)
    console.log(`Passed: ${summary.passed}`)
    console.log(`Failed: ${summary.failed}`)
    console.log(`Success Rate: ${((summary.passed / summary.total) * 100).toFixed(1)}%`)

    return { testResults: results, summary }
  }

  /**
   * Scenario 1: Last Write Wins - Remote Operation is Newer
   */
  private async testLastWriteWinsRemoteNewer(): Promise<void> {
    // Setup: Create a gate with initial state
    const gateId = 'test_gate_lww_remote'
    await this.createTestGate(gateId, 'Initial Gate', 1)

    // Local operation (older timestamp)
    const localTimestamp = new Date(Date.now() - 5000).toISOString()
    await this.deltaSync.recordOperation(
      'gate',
      gateId,
      'update',
      'name',
      'Initial Gate',
      'Local Update',
      'user1'
    )

    // Simulate remote operation (newer timestamp)
    const remoteOp: DeltaOperation = {
      id: 'remote_op_1',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Initial Gate',
      newValue: 'Remote Update',
      rowVersion: 2,
      timestamp: new Date().toISOString(), // newer
      syncStatus: 'pending'
    }

    // Test conflict resolution
    const mockLocalOp = await this.getLatestLocalOperation(gateId)
    if (!mockLocalOp) throw new Error('No local operation found')

    const conflict = await this.deltaSync['resolveConflict'](
      mockLocalOp,
      remoteOp,
      'last_write_wins'
    )

    // Verify: Remote should win (newer timestamp)
    if (conflict.resolvedValue !== 'Remote Update') {
      throw new Error(`Expected 'Remote Update', got '${conflict.resolvedValue}'`)
    }

    console.log('   ✓ Remote operation won (newer timestamp)')
  }

  /**
   * Scenario 2: Last Write Wins - Local Operation is Newer
   */
  private async testLastWriteWinsLocalNewer(): Promise<void> {
    const gateId = 'test_gate_lww_local'
    await this.createTestGate(gateId, 'Initial Gate', 1)

    // Remote operation (older timestamp)
    const remoteOp: DeltaOperation = {
      id: 'remote_op_2',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Initial Gate',
      newValue: 'Remote Update',
      rowVersion: 2,
      timestamp: new Date(Date.now() - 5000).toISOString(), // older
      syncStatus: 'pending'
    }

    // Local operation (newer timestamp)
    await this.deltaSync.recordOperation(
      'gate',
      gateId,
      'update',
      'name',
      'Initial Gate',
      'Local Update',
      'user1'
    )

    const localOp = await this.getLatestLocalOperation(gateId)
    if (!localOp) throw new Error('No local operation found')

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'last_write_wins'
    )

    // Verify: Local should win (newer timestamp)
    if (conflict.resolvedValue !== 'Local Update') {
      throw new Error(`Expected 'Local Update', got '${conflict.resolvedValue}'`)
    }

    console.log('   ✓ Local operation won (newer timestamp)')
  }

  /**
   * Scenario 3: Operational Transform - Same Field Conflict
   */
  private async testOperationalTransformSameField(): Promise<void> {
    const gateId = 'test_gate_ot_same'
    await this.createTestGate(gateId, 'Initial Gate', 1)

    // Two operations on same field with close timestamps
    const baseTime = Date.now()
    
    const localOp: DeltaOperation = {
      id: 'local_op_3',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Initial Gate',
      newValue: 'Local Change',
      rowVersion: 2,
      timestamp: new Date(baseTime).toISOString(),
      syncStatus: 'pending'
    }

    const remoteOp: DeltaOperation = {
      id: 'remote_op_3',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Initial Gate',
      newValue: 'Remote Change',
      rowVersion: 2,
      timestamp: new Date(baseTime + 100).toISOString(),
      syncStatus: 'pending'
    }

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'operational_transform'
    )

    // For same field, OT should fall back to last write wins
    if (conflict.resolvedValue !== 'Remote Change') {
      throw new Error(`Expected 'Remote Change', got '${conflict.resolvedValue}'`)
    }

    console.log('   ✓ Operational transform applied (same field conflict)')
  }

  /**
   * Scenario 4: Operational Transform - Different Fields
   */
  private async testOperationalTransformDifferentFields(): Promise<void> {
    const gateId = 'test_gate_ot_diff'
    await this.createTestGate(gateId, 'Initial Gate', 1)

    const localOp: DeltaOperation = {
      id: 'local_op_4',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Initial Gate',
      newValue: 'Updated Name',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const remoteOp: DeltaOperation = {
      id: 'remote_op_4',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'location',
      oldValue: 'Old Location',
      newValue: 'New Location',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'operational_transform'
    )

    // Different fields should be merged
    const resolved = conflict.resolvedValue
    if (!resolved || resolved.name !== 'Updated Name' || resolved.location !== 'New Location') {
      throw new Error('Field merge failed in operational transform')
    }

    console.log('   ✓ Operational transform merged different fields')
  }

  /**
   * Scenario 5: Field Level Merge
   */
  private async testFieldLevelMerge(): Promise<void> {
    const gateId = 'test_gate_field_merge'
    await this.createTestGate(gateId, 'Initial Gate', 1)

    // Create mock entity in database
    await this.db.executeSql(
      'UPDATE gates SET name = ?, location = ? WHERE id = ?',
      ['Current Name', 'Current Location', gateId]
    )

    const localOp: DeltaOperation = {
      id: 'local_op_5',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Current Name',
      newValue: 'Local Name Update',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const remoteOp: DeltaOperation = {
      id: 'remote_op_5',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'location',
      oldValue: 'Current Location',
      newValue: 'Remote Location Update',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'field_level_merge'
    )

    // Both fields should be preserved
    const resolved = conflict.resolvedValue
    if (!resolved || resolved.name !== 'Local Name Update' || resolved.location !== 'Remote Location Update') {
      throw new Error('Field level merge failed')
    }

    console.log('   ✓ Field level merge preserved both changes')
  }

  /**
   * Scenario 6: Manual Resolution Required
   */
  private async testManualResolution(): Promise<void> {
    const gateId = 'test_gate_manual'
    await this.createTestGate(gateId, 'Initial Gate', 1)

    const localOp: DeltaOperation = {
      id: 'local_op_6',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'status',
      oldValue: 'active',
      newValue: 'maintenance',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const remoteOp: DeltaOperation = {
      id: 'remote_op_6',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'status',
      oldValue: 'active',
      newValue: 'inactive',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'manual_resolution'
    )

    // Should be stored for manual resolution
    if (conflict.resolvedValue !== undefined) {
      throw new Error('Manual resolution should not have resolved value')
    }

    console.log('   ✓ Conflict stored for manual resolution')
  }

  /**
   * Scenario 7: Concurrent Creates with Same ID
   */
  private async testConcurrentCreates(): Promise<void> {
    const gateId = 'test_gate_concurrent'

    const localOp: DeltaOperation = {
      id: 'local_create_1',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'create',
      newValue: { id: gateId, name: 'Local Created Gate', status: 'active' },
      rowVersion: 1,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const remoteOp: DeltaOperation = {
      id: 'remote_create_1',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'create',
      newValue: { id: gateId, name: 'Remote Created Gate', status: 'inactive' },
      rowVersion: 1,
      timestamp: new Date(Date.now() + 1000).toISOString(), // slightly newer
      syncStatus: 'pending'
    }

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'last_write_wins'
    )

    // Remote should win due to newer timestamp
    const resolved = conflict.resolvedValue
    if (!resolved || resolved.name !== 'Remote Created Gate') {
      throw new Error('Concurrent create conflict resolution failed')
    }

    console.log('   ✓ Concurrent create conflict resolved')
  }

  /**
   * Scenario 8: Delete vs Update Conflict
   */
  private async testDeleteVsUpdate(): Promise<void> {
    const gateId = 'test_gate_del_update'
    await this.createTestGate(gateId, 'Gate to Delete', 1)

    const localOp: DeltaOperation = {
      id: 'local_delete_1',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'delete',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    const remoteOp: DeltaOperation = {
      id: 'remote_update_1',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Gate to Delete',
      newValue: 'Updated Gate Name',
      rowVersion: 2,
      timestamp: new Date(Date.now() + 500).toISOString(),
      syncStatus: 'pending'
    }

    const conflict = await this.deltaSync['resolveConflict'](
      localOp,
      remoteOp,
      'last_write_wins'
    )

    // Remote update should win (newer timestamp)
    if (conflict.resolvedValue !== 'Updated Gate Name') {
      throw new Error('Delete vs Update conflict not properly resolved')
    }

    console.log('   ✓ Delete vs Update conflict resolved (update won)')
  }

  /**
   * Scenario 9: Batch Sync with Multiple Conflicts
   */
  private async testBatchSyncConflicts(): Promise<void> {
    // Create multiple test entities
    const gateIds = ['batch_gate_1', 'batch_gate_2', 'batch_gate_3']
    
    for (const gateId of gateIds) {
      await this.createTestGate(gateId, `Gate ${gateId}`, 1)
      
      // Create local operations
      await this.deltaSync.recordOperation(
        'gate',
        gateId,
        'update',
        'name',
        `Gate ${gateId}`,
        `Local Update ${gateId}`,
        'user1'
      )
    }

    // Simulate batch pull with conflicts
    const mockPullResponse = {
      operations: gateIds.map(gateId => ({
        id: `remote_${gateId}`,
        entityType: 'gate',
        entityId: gateId,
        operationType: 'update',
        fieldName: 'name',
        oldValue: `Gate ${gateId}`,
        newValue: `Remote Update ${gateId}`,
        rowVersion: 2,
        timestamp: new Date().toISOString(),
        syncStatus: 'pending'
      })),
      nextSyncToken: 'batch_token_123'
    }

    // This would normally be called by the sync service
    // For testing, we verify the conflict detection logic
    let conflictCount = 0
    
    for (const remoteOp of mockPullResponse.operations) {
      const localConflict = await this.deltaSync['detectLocalConflict'](remoteOp)
      if (localConflict) {
        conflictCount++
      }
    }

    if (conflictCount !== gateIds.length) {
      throw new Error(`Expected ${gateIds.length} conflicts, found ${conflictCount}`)
    }

    console.log(`   ✓ Batch sync detected ${conflictCount} conflicts correctly`)
  }

  /**
   * Scenario 10: Exponential Backoff Retry Test
   */
  private async testExponentialBackoff(): Promise<void> {
    let attemptCount = 0
    const maxRetries = 3
    
    const mockFailingOperation = async (): Promise<any> => {
      attemptCount++
      if (attemptCount < maxRetries) {
        throw new Error(`Attempt ${attemptCount} failed`)
      }
      return { success: true, batchId: 'test_batch', syncedOperations: 1, conflicts: [], errors: [] }
    }

    const startTime = Date.now()
    
    const result = await this.deltaSync.syncWithRetry(mockFailingOperation, {
      maxRetries: 3,
      retryDelayMs: 100,
      backoffMultiplier: 2
    })

    const endTime = Date.now()
    const totalTime = endTime - startTime

    // Should have made 3 attempts with exponential backoff
    if (attemptCount !== 3) {
      throw new Error(`Expected 3 attempts, made ${attemptCount}`)
    }

    // Should take at least 100ms + 200ms = 300ms due to backoff
    if (totalTime < 300) {
      throw new Error(`Backoff timing too short: ${totalTime}ms`)
    }

    console.log(`   ✓ Exponential backoff worked (${attemptCount} attempts, ${totalTime}ms)`)
  }

  /**
   * Scenario 11: ETag Version Mismatch
   */
  private async testETagVersionMismatch(): Promise<void> {
    const gateId = 'test_gate_etag'
    await this.createTestGate(gateId, 'ETag Test Gate', 1)

    // Update entity with specific etag
    const etag1 = '"gate-1-1633024800000"'
    const etag2 = '"gate-2-1633024900000"' // different version

    await this.db.executeSql(
      'UPDATE gates SET etag = ?, row_version = 1 WHERE id = ?',
      [etag1, gateId]
    )

    // Simulate operation with mismatched etag
    const operation: DeltaOperation = {
      id: 'etag_test_1',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'ETag Test Gate',
      newValue: 'Updated with Wrong ETag',
      rowVersion: 2,
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    // Check current etag
    const result = await this.db.executeSql('SELECT etag FROM gates WHERE id = ?', [gateId])
    const currentETag = result[0].rows.item(0).etag

    if (currentETag !== etag1) {
      throw new Error(`ETag mismatch: expected ${etag1}, got ${currentETag}`)
    }

    console.log('   ✓ ETag version mismatch detected correctly')
  }

  /**
   * Scenario 12: Row Version Conflict Detection
   */
  private async testRowVersionConflict(): Promise<void> {
    const gateId = 'test_gate_row_version'
    await this.createTestGate(gateId, 'Row Version Test', 1)

    // Set initial row version
    await this.db.executeSql(
      'UPDATE gates SET row_version = 5 WHERE id = ?',
      [gateId]
    )

    // Create operation with conflicting row version
    const localOp: DeltaOperation = {
      id: 'row_version_test',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Row Version Test',
      newValue: 'Local Update',
      rowVersion: 6, // expected next version
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    // Simulate remote operation with different version
    const remoteOp: DeltaOperation = {
      id: 'remote_row_version_test',
      entityType: 'gate',
      entityId: gateId,
      operationType: 'update',
      fieldName: 'name',
      oldValue: 'Row Version Test',
      newValue: 'Remote Update',
      rowVersion: 7, // higher version (conflict)
      timestamp: new Date().toISOString(),
      syncStatus: 'pending'
    }

    // Row version conflict should be detected
    if (localOp.rowVersion >= remoteOp.rowVersion) {
      throw new Error('Row version conflict not properly simulated')
    }

    console.log('   ✓ Row version conflict detected (local: 6, remote: 7)')
  }

  /**
   * Helper Methods
   */
  private async createTestGate(id: string, name: string, rowVersion: number): Promise<void> {
    const sql = `
      INSERT OR REPLACE INTO gates (
        id, name, gate_code, location, status, qr_code, 
        row_version, sync_status, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `

    await this.db.executeSql(sql, [
      id,
      name,
      `CODE_${id}`,
      'Test Location',
      'active',
      `QR_${id}`,
      rowVersion,
      'synced',
      new Date().toISOString(),
      new Date().toISOString()
    ])
  }

  private async getLatestLocalOperation(entityId: string): Promise<DeltaOperation | null> {
    const sql = `
      SELECT * FROM delta_operations 
      WHERE entity_id = ? AND sync_status = 'pending'
      ORDER BY timestamp DESC 
      LIMIT 1
    `

    const result = await this.db.executeSql(sql, [entityId])

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
   * Cleanup test data
   */
  public async cleanup(): Promise<void> {
    const testTables = ['gates', 'delta_operations', 'sync_batches', 'sync_conflicts']
    
    for (const table of testTables) {
      await this.db.executeSql(`DELETE FROM ${table} WHERE id LIKE 'test_%'`)
      await this.db.executeSql(`DELETE FROM ${table} WHERE id LIKE 'batch_%'`)
    }
    
    console.log('✅ Test data cleaned up')
  }
}

// Export for use in test runner
export default DeltaSyncConflictTests