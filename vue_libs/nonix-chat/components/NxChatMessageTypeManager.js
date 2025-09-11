import {markRaw} from 'vue';
import NxBaseWidgetManager from '@nonix/widget-manager/NxBaseWidgetManager.js';

/**
 * NxChatMessageTypeManager - Registry for managing different chat message type components
 * Extends NxBaseWidgetManager to provide dynamic message rendering capabilities
 */
class NxChatMessageTypeManager extends NxBaseWidgetManager {
    constructor() {
        super();
        this.messageTypes = new Map();
        this.defaultMessageType = 'text';
    }

    /**
     * Register a new message type component
     * @param {string} type - The message type identifier
     * @param {Object} component - The Vue component to register
     */
    registerMessageType(type, component) {
        if (!type || typeof type !== 'string') {
            throw new Error('Message type must be a non-empty string');
        }

        if (!component) {
            throw new Error('Component is required');
        }

        this.messageTypes.set(type, markRaw(component));
        console.log(`Registered message type: ${type}`);
    }

    /**
     * Get a message type component by type
     * @param {string} type - The message type identifier
     * @returns {Object|null} The registered component or null if not found
     */
    getMessageType(type) {
        return this.messageTypes.get(type) || this.messageTypes.get(this.defaultMessageType);
    }

    /**
     * Get all registered message types
     * @returns {Array} Array of registered message type identifiers
     */
    getAllMessageTypes() {
        return Array.from(this.messageTypes.keys());
    }

    /**
     * Check if a message type is registered
     * @param {string} type - The message type identifier
     * @returns {boolean} True if registered, false otherwise
     */
    hasMessageType(type) {
        return this.messageTypes.has(type);
    }

    /**
     * Unregister a message type
     * @param {string} type - The message type identifier to remove
     */
    unregisterMessageType(type) {
        if (this.messageTypes.has(type)) {
            this.messageTypes.delete(type);
            console.log(`Unregistered message type: ${type}`);
        }
    }

    /**
     * Get the default message type
     * @returns {string} The default message type identifier
     */
    getDefaultMessageType() {
        return this.defaultMessageType;
    }

    /**
     * Set the default message type
     * @param {string} type - The new default message type identifier
     */
    setDefaultMessageType(type) {
        if (this.messageTypes.has(type)) {
            this.defaultMessageType = type;
        } else {
            throw new Error(`Cannot set default message type: ${type} is not registered`);
        }
    }

    /**
     * Get the count of registered message types
     * @returns {number} Number of registered message types
     */
    getMessageTypeCount() {
        return this.messageTypes.size;
    }

    /**
     * Clear all registered message types
     */
    clearMessageTypes() {
        this.messageTypes.clear();
        console.log('All message types cleared');
    }
}

// Create and export singleton instance
const chatMessageTypeManager = new NxChatMessageTypeManager();
export default chatMessageTypeManager;
