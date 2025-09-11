import { useToast } from 'primevue/usetoast';

/**
 * Composable for handling message editing logic
 * DRY - Don't Repeat Yourself - reusable across all message types
 *
 * @param {Object} chatService - The injected chat service instance
 */
export function useNxChatMessageEdit(chatService) {
  const toast = useToast();

  /**
   * Handle message editing with backend call, validation, and UI feedback
   * @param {Object} editData - The edit data from NxChatMessageEditMode
   * @param {Object} props - Component props containing sessionId, historyId
   * @param {Function} emit - Vue emit function
   * @param {string} componentName - Name of the component for logging
   */
  const handleEdit = async (editData, props, emit, componentName) => {
    try {
      console.info(`📝 ${componentName}: Processing edit and calling backend directly`, {
        messageId: editData.messageId,
        contentLength: editData.newContent?.length || 0
      });

      // Call backend directly
      const updatedMessage = await chatService.updateMessage(
        props.sessionId,
        props.historyId,
        editData.messageId,
        { content_json: { text: editData.newContent } }
      );

      console.info(`✅ ${componentName}: Backend update successful`, {
        messageId: updatedMessage?.id,
        updatedAt: updatedMessage?.updated_at
      });

      // Show success toast
      toast.add({
        severity: 'success',
        summary: 'Message Updated',
        detail: 'Your message has been saved successfully',
        life: 2000
      });

      // Emit success event (container can handle UI updates if needed)
      emit('edit-success');

    } catch (error) {
      console.error(`❌ ${componentName}: Edit failed`, error);

      // Show error toast
      toast.add({
        severity: 'error',
        summary: 'Edit Failed',
        detail: 'Failed to update message. Please try again.',
        life: 3000
      });
    }
  };

  return {
    handleEdit
  };
}
