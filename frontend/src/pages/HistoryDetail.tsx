import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import ChatInterface from '../components/features/ChatInterface';
import { Trash2, AlertTriangle } from 'lucide-react';
import { useMutation } from "convex/react";
import { api } from "../../convex/_generated/api";
import type { Id } from "../../convex/_generated/dataModel";
import { useAuth } from '../hooks/useAuth';

const HistoryDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const { isLocalMode } = useAuth();
  const removeConversation = useMutation(api.conversations.remove);

  const handleDelete = async () => {
    if (!id) return;
    setIsDeleting(true);
    try {
      if (isLocalMode || id.startsWith('local-')) {
        // Delete from localStorage
        const localHistory = JSON.parse(localStorage.getItem('psypredict_local_history') || '{}');
        delete localHistory[id];
        localStorage.setItem('psypredict_local_history', JSON.stringify(localHistory));
      } else {
        // Delete from Convex (cascade delete handled server-side)
        await removeConversation({ id: id as Id<"conversations"> });
      }
      
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
