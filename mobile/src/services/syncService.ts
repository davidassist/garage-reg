/**
 * Sync Service - Handles offline/online data synchronization
 * Conflict resolution and background sync
 */

import AsyncStorage from '@react-native-async-storage/async-storage'
import NetInfo, { NetInfoState } from '@react-native-netinfo/netinfo'
import { GatesRepository } from '../storage/gatesRepository'
import { InspectionsRepository } from '../storage/inspectionsRepository'
import { APIService } from './apiService'
import {
  Gate,
  Inspection,
  SyncStatus,
  SyncConflict,
  ConflictResolution,
  QueueItem,
  NetworkState
} from '../types'

export interface SyncResult {
  success: boolean
  syncedItems: number
  conflicts: SyncConflict[]
  errors: string[]
}

export class SyncService {
  private static instance: SyncService
  private gatesRepo = new GatesRepository()
  private inspectionsRepo = new InspectionsRepository()
  private apiService = new APIService()
  private isSyncing = false
  private syncQueue: QueueItem[] = []
  private networkState: NetworkState = {
    isConnected: false,
    connectionType: 'none',
    isWifiEnabled: false,
    strength: 0
  }

  public static getInstance(): SyncService {
    if (!SyncService.instance) {
      SyncService.instance = new SyncService()
    }
    return SyncService.instance
  }

  constructor() {
    this.initializeNetworkMonitoring()
  }

  /**
   * Initialize network state monitoring
   */
  private initializeNetworkMonitoring(): void {
    NetInfo.addEventListener((state: NetInfoState) => {
      const wasConnected = this.networkState.isConnected
      
      this.networkState = {
        isConnected: state.isConnected || false,
        connectionType: state.type || 'none',
        isWifiEnabled: state.type === 'wifi',
        strength: this.getSignalStrength(state)
      }

      // Auto-sync when connection is restored
      if (!wasConnected && this.networkState.isConnected) {
        this.triggerAutoSync()
      }
    })
  }

  /**
   * Get signal strength from network state
   */
  private getSignalStrength(state: NetInfoState): number {
    if (state.details && 'strength' in state.details) {
      return (state.details.strength as number) || 0
    }
    return state.isConnected ? 3 : 0
  }

  /**
   * Check if device is online
   */
  public isOnline(): boolean {
    return this.networkState.isConnected
  }

  /**
   * Get current network state
   */
  public getNetworkState(): NetworkState {
    return this.networkState
  }

  /**
   * Manual sync trigger
   */
  public async syncNow(): Promise<SyncResult> {
    if (this.isSyncing) {
      throw new Error('Sync already in progress')
    }

    if (!this.isOnline()) {
      throw new Error('No internet connection')
    }

    this.isSyncing = true
    
    try {
      const result = await this.performSync()
      await this.updateLastSyncTime()
      return result
    } finally {
      this.isSyncing = false
    }
  }

  /**
   * Auto sync when conditions are met
   */
  private async triggerAutoSync(): Promise<void> {
    const settings = await this.getAppSettings()
    
    if (!settings.autoSync) return
    if (settings.syncOnWifiOnly && !this.networkState.isWifiEnabled) return
    
    try {
      await this.syncNow()
    } catch (error) {
      // Auto sync failed silently
    }
  }

  /**
   * Perform full synchronization
   */
  private async performSync(): Promise<SyncResult> {
    const result: SyncResult = {
      success: true,
      syncedItems: 0,
      conflicts: [],
      errors: []
    }

    try {
      // 1. Download fresh data from server
      await this.downloadServerData(result)
      
      // 2. Upload local changes
      await this.uploadLocalChanges(result)
      
      // 3. Process sync queue
      await this.processSyncQueue(result)
      
    } catch (error) {
      result.success = false
      result.errors.push(error instanceof Error ? error.message : 'Unknown sync error')
    }

    return result
  }

  /**
   * Download fresh data from server
   */
  private async downloadServerData(result: SyncResult): Promise<void> {
    try {
      // Download gates
      const serverGates = await this.apiService.getGates()
      for (const serverGate of serverGates) {
        await this.syncGate(serverGate, result)
      }

      // Download inspection templates
      const templates = await this.apiService.getInspectionTemplates()
      // Store templates in local storage
      
    } catch (error) {
      result.errors.push(`Download failed: ${error}`)
    }
  }

  /**
   * Upload local changes to server
   */
  private async uploadLocalChanges(result: SyncResult): Promise<void> {
    try {
      // Upload pending inspections
      const pendingInspections = await this.inspectionsRepo.getPendingSync()
      
      for (const inspection of pendingInspections) {
        await this.syncInspection(inspection, result)
      }

      // Upload photos
      await this.uploadPendingPhotos(result)
      
    } catch (error) {
      result.errors.push(`Upload failed: ${error}`)
    }
  }

  /**
   * Sync individual gate with conflict detection
   */
  private async syncGate(serverGate: Gate, result: SyncResult): Promise<void> {
    const localGate = await this.gatesRepo.getById(serverGate.id)
    
    if (!localGate) {
      // New gate from server
      await this.gatesRepo.upsert({ ...serverGate, syncStatus: 'synced' })
      result.syncedItems++
      return
    }

    // Check for conflicts
    const conflict = this.detectGateConflict(localGate, serverGate)
    if (conflict) {
      result.conflicts.push(conflict)
      return
    }

    // No conflict, update local gate
    await this.gatesRepo.upsert({ ...serverGate, syncStatus: 'synced' })
    result.syncedItems++
  }

  /**
   * Detect conflicts between local and server gate data
   */
  private detectGateConflict(local: Gate, server: Gate): SyncConflict | null {
    const localTime = new Date(local.lastSyncAt || local.updatedAt || 0)
    const serverTime = new Date(server.lastSyncAt || server.updatedAt || 0)
    
    // Check if both have been modified since last sync
    if (local.syncStatus === 'pending' && serverTime > localTime) {
      return {
        id: `conflict_${Date.now()}`,
        entityType: 'gate',
        entityId: local.id,
        field: 'data',
        localValue: local,
        remoteValue: server,
        localTimestamp: localTime.toISOString(),
        remoteTimestamp: serverTime.toISOString()
      }
    }

    return null
  }

  /**
   * Sync individual inspection
   */
  private async syncInspection(inspection: Inspection, result: SyncResult): Promise<void> {
    try {
      if (inspection.syncStatus === 'pending') {
        // Upload to server
        await this.apiService.createOrUpdateInspection(inspection)
        await this.inspectionsRepo.updateSyncStatus(inspection.id, 'synced')
        result.syncedItems++
      }
    } catch (error) {
      await this.inspectionsRepo.updateSyncStatus(inspection.id, 'error')
      result.errors.push(`Inspection sync failed: ${inspection.id}`)
    }
  }

  /**
   * Upload pending photos
   */
  private async uploadPendingPhotos(result: SyncResult): Promise<void> {
    // Implementation for photo upload queue
    // This would handle background photo uploads
  }

  /**
   * Process sync queue items
   */
  private async processSyncQueue(result: SyncResult): Promise<void> {
    // Process queued sync operations
    for (const item of this.syncQueue) {
      try {
        await this.processQueueItem(item)
        result.syncedItems++
      } catch (error) {
        result.errors.push(`Queue item failed: ${item.id}`)
      }
    }
    
    this.syncQueue = []
  }

  /**
   * Process individual queue item
   */
  private async processQueueItem(item: QueueItem): Promise<void> {
    switch (item.type) {
      case 'inspection':
        // Handle inspection sync
        break
      case 'photo':
        // Handle photo upload
        break
      case 'gate_data':
        // Handle gate data sync
        break
    }
  }

  /**
   * Resolve sync conflict
   */
  public async resolveConflict(
    conflictId: string,
    resolution: ConflictResolution,
    resolvedBy: string
  ): Promise<void> {
    // Implementation for conflict resolution
    // This would update the local database with the resolved value
  }

  /**
   * Add item to sync queue
   */
  public addToQueue(item: Omit<QueueItem, 'id' | 'createdAt'>): void {
    const queueItem: QueueItem = {
      ...item,
      id: `queue_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date().toISOString(),
      status: 'pending'
    }
    
    this.syncQueue.push(queueItem)
  }

  /**
   * Get sync status
   */
  public async getSyncStatus(): Promise<{
    lastSyncAt?: string
    isSyncing: boolean
    pendingItems: number
    conflicts: number
  }> {
    const lastSyncAt = await AsyncStorage.getItem('last_sync_at')
    const pendingInspections = await this.inspectionsRepo.getPendingSync()
    
    return {
      lastSyncAt: lastSyncAt || undefined,
      isSyncing: this.isSyncing,
      pendingItems: pendingInspections.length + this.syncQueue.length,
      conflicts: 0 // Would query conflicts table
    }
  }

  /**
   * Update last sync time
   */
  private async updateLastSyncTime(): Promise<void> {
    await AsyncStorage.setItem('last_sync_at', new Date().toISOString())
  }

  /**
   * Get app settings
   */
  private async getAppSettings(): Promise<{
    autoSync: boolean
    syncOnWifiOnly: boolean
  }> {
    const autoSync = await AsyncStorage.getItem('auto_sync')
    const syncOnWifiOnly = await AsyncStorage.getItem('sync_on_wifi_only')
    
    return {
      autoSync: autoSync !== 'false',
      syncOnWifiOnly: syncOnWifiOnly === 'true'
    }
  }

  /**
   * Force sync all data (for testing)
   */
  public async forceSyncAll(): Promise<SyncResult> {
    // Mark all local data as pending and sync
    const gates = await this.gatesRepo.getAll()
    for (const gate of gates) {
      await this.gatesRepo.updateSyncStatus(gate.id, 'pending')
    }

    const inspections = await this.inspectionsRepo.getAll()
    for (const inspection of inspections) {
      await this.inspectionsRepo.updateSyncStatus(inspection.id, 'pending')
    }

    return this.syncNow()
  }
}