import React, { useEffect, useState } from 'react';
import Navbar from '../components/common/Navbar';
import { useUser } from '@clerk/react';
import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";
import { Link } from 'react-router-dom';
import { MessageSquare, Calendar, ChevronRight, Clock } from 'lucide-react';
import { useGuestMode } from '../context/GuestModeContext';


const History: React.FC = () => {
    const { user } = useUser();
    const { isGuestMode, guestConversations } = useGuestMode();
    const [conversations, setConversations] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // Convex query — skipped entirely in guest mode
    const convexConversations = useQuery(
        api.conversations.list,
        !isGuestMode && user ? {} : "skip"
    );

    useEffect(() => {
        if (isGuestMode) {
            const sorted = [...guestConversations]
                .map((c) => ({
                    id: c.id,
                    title: c.title,
                    created_at: c.createdAt,
                }))
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
            setConversations(sorted);
            setLoading(false);
            return;
        }

        if (!user) return;

        if (convexConversations) {
            const sorted = [...convexConversations]
                .map((c: any) => ({
                    id: c._id,
                    title: c.title,
                    created_at: c.createdAt,
                }))
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
            setConversations(sorted);
        }
        setLoading(false);
    }, [user, convexConversations, isGuestMode, guestConversations]);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />

            <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">Consultation History</h1>
                    <p className="text-gray-500 mt-2">View your past conversations and generated prescriptions.</p>
                </div>

                {/* Guest mode notice */}
                {isGuestMode && (
                    <div className="mb-6 flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                        <Clock size={16} className="text-amber-600 mt-0.5 shrink-0" />
                        <p className="text-sm text-amber-700">
                            <span className="font-semibold">Guest Mode:</span> Your conversations are stored temporarily in this session only.
                            They will be lost when you close the tab or sign in.
                        </p>
                    </div>
                )}

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
                                        <div className="flex items-center gap-2 mb-1">
                                            <h3 className="font-semibold text-gray-900">{conv.title || 'Untitled Conversation'}</h3>
                                            {isGuestMode && (
                                                <span className="text-[10px] font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                                                    Temporary
                                                </span>
                                            )}
                                        </div>
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
