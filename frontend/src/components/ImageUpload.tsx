'use client';

import { useState, useRef } from 'react';
import { Upload, X, Loader2, Image as ImageIcon } from 'lucide-react';
import api from '@/lib/api';

interface Props {
  value: string;
  onChange: (url: string) => void;
  type?: 'articles' | 'news_images' | 'general';
  disabled?: boolean;
}

export default function ImageUpload({ value, onChange, type = 'articles', disabled = false }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const upload = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Sadece gorsel dosyalari yuklenebilir.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('Dosya boyutu 5MB\'dan buyuk olamaz.');
      return;
    }

    setError('');
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('type', type);
      const { data } = await api.post('/content/upload-image/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (data.success) {
        onChange(data.url);
      } else {
        setError(data.error || 'Yukleme hatasi');
      }
    } catch (e: any) {
      setError(e.response?.data?.error || 'Yukleme basarisiz');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  };

  return (
    <div>
      {value ? (
        <div className="relative rounded-lg overflow-hidden border bg-gray-50">
          <img src={value} alt="" className="w-full max-h-48 object-cover" />
          {!disabled && (
            <button onClick={() => onChange('')} type="button"
              className="absolute top-2 right-2 p-1 rounded-full bg-red-500 text-white hover:bg-red-600 shadow">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      ) : (
        <div
          onDragOver={e => { e.preventDefault(); if (!disabled) setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !disabled && inputRef.current?.click()}
          className={'flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 cursor-pointer transition-colors ' +
            (dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50') +
            (disabled ? ' opacity-50 cursor-not-allowed' : '')}
        >
          {uploading ? (
            <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
          ) : (
            <ImageIcon className="h-8 w-8 text-gray-400" />
          )}
          <p className="text-sm text-gray-500">
            {uploading ? 'Yukleniyor...' : 'Surukle birak veya tikla'}
          </p>
          <p className="text-xs text-gray-400">JPEG, PNG, WebP, GIF - Max 5MB</p>
        </div>
      )}
      <input ref={inputRef} type="file" accept="image/*" hidden
        onChange={e => { const f = e.target.files?.[0]; if (f) upload(f); e.target.value = ''; }} />
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
}
