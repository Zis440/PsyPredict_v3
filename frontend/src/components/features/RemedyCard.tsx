// src/components/features/RemedyCard.tsx

import React, { useState, useEffect } from 'react';
import { getGitaAdvice } from '../../services/api';

interface RemedyProps {
  emotion: string;
}

const RemedyCard: React.FC<RemedyProps> = ({ emotion }) => {
  const [remedy, setRemedy] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Map emotions to CSV conditions roughly
  const mapEmotionToCondition = (emo: string) => {
    const map: {[key: string]: string} = {
      'sad': 'Depression',
      'fear': 'Anxiety',
      'angry': 'Bipolar Disorder', // Loose mapping for demo
      'neutral': 'Anxiety',        // Default fallback
      'happy': 'Anxiety'           // Default fallback
    };
    return map[emo.toLowerCase()] || 'Anxiety';
  };

  const fetchRemedy = async () => {
    setLoading(true);
    try {
      const condition = mapEmotionToCondition(emotion);
      const data = await getGitaAdvice(condition);
      setRemedy(data);
    } catch (err) {
      console.error("Failed to get remedy", err);
    } finally {
      setLoading(false);
    }
  };

  // Automatically fetch when emotion changes (optional) or keep manual
  useEffect(() => {
    if (emotion !== 'neutral') {
      fetchRemedy();
    }
  }, [emotion]);

  if (loading) return <div className="p-4 text-gray-500 animate-pulse">Consulting the Gita...</div>;

  if (!remedy) return (
    <div className="p-6 bg-yellow-50 rounded-xl border border-yellow-200 text-center">
      <p className="text-yellow-800 font-semibold">Ancient Wisdom</p>
      <p className="text-sm text-yellow-600 mt-1">Detecting emotion to find a remedy...</p>
    </div>
  );

  return (
    <div className="bg-amber-50 p-6 rounded-xl border border-amber-200 shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-bold text-orange-900">🌿 Ancient Wisdom</h3>
        <span className="text-xs bg-orange-200 text-orange-800 px-2 py-1 rounded-md">{remedy.condition}</span>
      </div>
      
      <p className="text-gray-700 italic text-sm mb-4">"{remedy.gita_remedy}"</p>
      
      <div className="bg-white p-3 rounded-lg text-sm text-gray-600 shadow-sm">
        <p><strong>Suggested Tip:</strong> {remedy.treatments}</p>
      </div>
    </div>
  );
};

export default RemedyCard;