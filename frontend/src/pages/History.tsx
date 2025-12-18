import React, { useEffect, useState } from 'react';
import Navbar from '../components/common/Navbar';
import { supabase } from '../lib/supabase';
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import { MessageSquare, Calendar, ChevronRight } from 'lucide-react';
import type { Database } from '../types/supabase';

type Conversation = Database['public']['Tables']['conversations']['Row'];

const History: React.FC = () => {
    const { user } = useAuth();
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) return;

        const fetchHistory = async () => {
            const { data, error } = await supabase
                .from('conversations')
                .select('*')
                .eq('user_id', user.id)
                .order('created_at', { ascending: false });

            if (error) {
                console.error('Error fetching history:', error);
            } else if (data) {
                setConversations(data);
            }
            setLoading(false);
        };

        fetchHistory();
    }, [user]);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />
            
            <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">Consultation History</h1>
                    <p className="text-gray-500 mt-2">View your past conversations and generated prescriptions.</p>
                </div>

                {loading ? (
                    <div className="flex justify-center py-12">
                       <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    </div>
                ) : conversations.length === 0 ? (
                    <div className="text-center py-16 bg-white rounded-2xl border border-gray-200 border-dashed">
                        <div className="bg-indigo-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <MessageSquare className="text-indigo-600" size={24} />
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">No conversations yet</h3>
                        <p className="text-gray-500 mt-1 mb-6">Start a new chat to track your mental wellness.</p>
                        <Link to="/dashboard" className="bg-indigo-600 text-white px-6 py-2 rounded-full font-medium hover:bg-indigo-700 transition-colors">
                            Start New Chat
                        </Link>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {conversations.map((conv) => (
                            <Link 
                                key={conv.id} 
                                to={`/history/${conv.id}`}
                                className="bg-white p-6 rounded-xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all group flex items-center justify-between"
                            >
                                <div className="flex items-start gap-4">
                                     <div className="bg-indigo-50 p-3 rounded-lg group-hover:bg-indigo-100 transition-colors">
                                        <MessageSquare className="text-indigo-600" size={20} />
                                     </div>
                                     <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">{conv.title || 'Untitled Conversation'}</h3>
                                        <div className="flex items-center gap-2 text-sm text-gray-500">
                                            <Calendar size={14} />
                                            {new Date(conv.created_at).toLocaleDateString(undefined, {
                                                weekday: 'short', 
                                                year: 'numeric', 
                                                month: 'short', 
                                                day: 'numeric'
                                            })}
                                            <span>•</span>
                                            {new Date(conv.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </div>
                                     </div>
                                </div>
                                <ChevronRight className="text-gray-300 group-hover:text-indigo-600 transition-colors" />
                            </Link>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};

export default History;
