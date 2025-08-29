import {ref} from 'vue'
import {io} from 'socket.io-client'

export default class WebSocketManager {
    constructor(app) {
        this.connectionState = ref('disconnected')
        this.socket = null
        this.app = app;
        this._initWebSocket()
    }

    // Initialize WebSocket - simple and direct
    _initWebSocket() {
        try {
            // Connect directly to backend
            this.socket = io( "ws://0.0.0.0:5000",{
                transports: ['websocket'],
                autoConnect: true,
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionAttempts: 5
            })

            this._setupSimpleEventHandlers()
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error)
            this.connectionState.value = 'disconnected'
        }
    }

    _setupSimpleEventHandlers() {
        if (!this.socket) return

        this.socket.on('connect', () => {
            console.log('🔌 WebSocket connected')
            this.connectionState.value = 'connected'
        })

        this.socket.on('disconnect', () => {
            console.log('🔌 WebSocket disconnected')
            this.connectionState.value = 'disconnected'
        })

        this.socket.on('connect_error', (error) => {
            console.error('🔌 WebSocket connection error:', error)
            this.connectionState.value = 'disconnected'
        })
    }

    joinRoom(room) {
        if (!this.socket?.connected) {
            console.warn('WebSocket not connected, cannot join room:', room)
            return false
        }

        this.socket.emit('join_room', room)
        console.log('🔌 Joined room:', room)
        return true
    }

    leaveRoom(room) {
        if (!this.socket?.connected) return false

        this.socket.emit('leave_room', room)
        console.log('🔌 Left room:', room)
        return true
    }

    on(event, callback) {
        if (!this.socket) return () => {
        }

        this.socket.on(event, callback)
        console.log('🔌 Listening to event:', event)

        // Return unsubscribe function
        return () => {
            if (this.socket) {
                this.socket.off(event, callback)
            }
        }
    }

    emit(event, data) {
        if (!this.socket?.connected) {
            console.warn('WebSocket not connected, cannot emit event:', event)
            return false
        }

        this.socket.emit(event, data)
        console.log('🔌 Emitted event:', event, data)
        return true
    }

    // Emit event to a specific room
    emitToRoom(room, event, data) {
        if (!this.socket?.connected) {
            console.warn('WebSocket not connected, cannot emit to room:', room)
            return false
        }

        this.socket.emit(event, data, room)
        console.log('🔌 Emitted to room:', room, 'event:', event, 'data:', data)
        return true
    }

    isConnected() {
        return this.socket?.connected && this.connectionState.value === 'connected'
    }

    getConnectionState() {
        return this.connectionState.value
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect()
            this.socket = null
        }
        this.connectionState.value = 'disconnected'
        console.log('🔌 WebSocket disconnected')
    }
}
