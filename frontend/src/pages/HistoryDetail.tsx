import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import ChatInterface from '../components/features/ChatInterface';
import { Trash2, AlertTriangle, X } from 'lucide-react';
import { supabase } from '../lib/supabase';

const HistoryDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!id) return;
    setIsDeleting(true);
    try {
      // 1. Delete all messages first (manual cascade)
      const { error: msgError } = await supabase
        .from('messages')
        .delete()
        .eq('conversation_id', id);

      if (msgError) throw msgError;

      // 2. Delete the conversation
      const { error } = await supabase
        .from('conversations')
        .delete()
        .eq('id', id);

      if (error) throw error;
      
      navigate('/history');
    } catch (error) {
      console.error('Error deleting conversation:', error);
      alert('Failed to delete conversation. Please try again.');
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100 overflow-hidden relative">
        <Navbar />
        
        <main className="flex-1 overflow-hidden px-4 py-4 md:px-6">
           <div className="max-w-5xl mx-auto h-full bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
               <div className="bg-gray-50 px-6 py-3 border-b border-gray-200 flex justify-between items-center shrink-0">
                   <h2 className="font-semibold text-gray-700">Historical Record</h2>
                   <div className="flex items-center gap-3">
                       <div className="text-xs text-amber-600 bg-amber-50 px-3 py-1 rounded-full font-medium border border-amber-200">
                           Viewing Past Session
                       </div>
                       <button 
                         onClick={() => setShowDeleteModal(true)}
                         className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                         title="Delete Conversation"
                       >
                         <Trash2 size={16} />
                       </button>
                   </div>
               </div>
               
               {/* 
                  Reuse ChatInterface with sessionId. 
                  Note: ChatInterface handles fetching logic.
                  We pass a static emotion for now or could fetch it if we stored it on conversation level.
               */}
               <div className="flex-1 min-h-0 bg-white min-w-0">
                  <ChatInterface currentEmotion="neutral" sessionId={id} />
               </div>
           </div>
        </main>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 transform transition-all scale-100 opacity-100">
              <div className="flex flex-col items-center text-center gap-4">
                <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600">
                  <AlertTriangle size={24} />
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-gray-900">Delete Conversation?</h3>
                  <p className="text-sm text-gray-500">
                    Are you sure you want to delete this session? This action cannot be undone.
                  </p>
                </div>

                <div className="flex gap-3 w-full mt-2">
                  <button
                    onClick={() => setShowDeleteModal(false)}
                    className="flex-1 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
                    disabled={isDeleting}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDelete}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    disabled={isDeleting}
                  >
                    {isDeleting ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default HistoryDetail;
