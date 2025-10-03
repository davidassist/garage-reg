/**
 * Login Screen - User authentication interface
 * Handles offline token storage and online authentication
 */

import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  StatusBar
} from 'react-native'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { APIService } from '../services/apiService'
import { User, AuthToken } from '../types'

interface LoginScreenProps {
  navigation: any
  onLoginSuccess: (user: User, token: AuthToken) => void
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ 
  navigation, 
  onLoginSuccess 
}) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isCheckingToken, setIsCheckingToken] = useState(true)

  const apiService = new APIService()

  useEffect(() => {
    checkStoredToken()
  }, [])

  /**
   * Check if user has valid stored token
   */
  const checkStoredToken = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('auth_token')
      const storedUser = await AsyncStorage.getItem('user_data')
      
      if (storedToken && storedUser) {
        const token = JSON.parse(storedToken)
        const user = JSON.parse(storedUser)
        
        // Check if token is still valid (not expired)
        const tokenExpiry = new Date(token.expiresAt)
        const now = new Date()
        
        if (tokenExpiry > now) {
          // Token is valid, auto-login
          apiService.setAuthToken(token.accessToken)
          onLoginSuccess(user, token)
          return
        } else {
          // Try to refresh token
          try {
            const newToken = await apiService.refreshToken(token.refreshToken)
            await AsyncStorage.setItem('auth_token', JSON.stringify(newToken))
            
            apiService.setAuthToken(newToken.accessToken)
            onLoginSuccess(user, newToken)
            return
          } catch (refreshError) {
            // Refresh failed, clear stored data
            await AsyncStorage.multiRemove(['auth_token', 'user_data'])
          }
        }
      }
    } catch (error) {
      // Error checking token, proceed with login
    } finally {
      setIsCheckingToken(false)
    }
  }

  /**
   * Handle user login
   */
  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Hiba', 'Kérjük adja meg a felhasználónevet és jelszót!')
      return
    }

    setIsLoading(true)

    try {
      const result = await apiService.login({
        username: username.trim(),
        password: password.trim()
      })

      // Store authentication data
      await AsyncStorage.multiSet([
        ['auth_token', JSON.stringify(result.token)],
        ['user_data', JSON.stringify(result.user)]
      ])

      // Clear password for security
      setPassword('')

      // Call success callback
      onLoginSuccess(result.user, result.token)

    } catch (error) {
      let message = 'Bejelentkezési hiba történt.'
      
      if (error instanceof Error) {
        // Handle specific error messages
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          message = 'Hibás felhasználónév vagy jelszó!'
        } else if (error.message.includes('Network')) {
          message = 'Nincs internetkapcsolat. Kérjük próbálja meg később!'
        }
      }

      Alert.alert('Bejelentkezési hiba', message)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Handle offline mode (for testing)
   */
  const handleOfflineMode = () => {
    Alert.alert(
      'Offline mód',
      'Offline módban korlátozott funkciók érhetők el. Folytatja?',
      [
        { text: 'Mégse', style: 'cancel' },
        { 
          text: 'Igen', 
          onPress: () => {
            // Mock user for offline mode
            const mockUser: User = {
              id: 'offline_user',
              username: 'offline',
              email: 'offline@example.com',
              fullName: 'Offline User',
              roles: [],
              permissions: [],
              lastLogin: new Date().toISOString()
            }
            
            const mockToken: AuthToken = {
              accessToken: 'offline_token',
              refreshToken: 'offline_refresh',
              expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
              tokenType: 'Bearer'
            }

            onLoginSuccess(mockUser, mockToken)
          }
        }
      ]
    )
  }

  // Show loading spinner while checking token
  if (isCheckingToken) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Ellenőrzés...</Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#007AFF" />
      
      <View style={styles.header}>
        <Text style={styles.title}>GarageReg</Text>
        <Text style={styles.subtitle}>Mobil Ellenőrzés</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.inputContainer}>
          <Text style={styles.label}>Felhasználónév</Text>
          <TextInput
            style={styles.input}
            value={username}
            onChangeText={setUsername}
            placeholder="Adja meg felhasználónevét"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!isLoading}
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Jelszó</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="Adja meg jelszavát"
            secureTextEntry
            editable={!isLoading}
            onSubmitEditing={handleLogin}
          />
        </View>

        <TouchableOpacity
          style={[styles.loginButton, isLoading && styles.disabledButton]}
          onPress={handleLogin}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator size="small" color="white" />
          ) : (
            <Text style={styles.loginButtonText}>Bejelentkezés</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.offlineButton}
          onPress={handleOfflineMode}
          disabled={isLoading}
        >
          <Text style={styles.offlineButtonText}>Offline mód</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>v1.0.0</Text>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: '#007AFF',
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  form: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  loginButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  offlineButton: {
    marginTop: 16,
    paddingVertical: 12,
    alignItems: 'center',
  },
  offlineButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '500',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
  },
})