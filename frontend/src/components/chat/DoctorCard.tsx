'use client';

import { User, BadgeCheck, MapPin, Building2 } from 'lucide-react';
import type { DoctorForChat } from '@/lib/types/chat';

interface DoctorCardProps {
  doctor: DoctorForChat;
  onSelect: (doctor: DoctorForChat) => void;
  selected?: boolean;
}

export default function DoctorCard({ doctor, onSelect, selected }: DoctorCardProps) {
  return (
    <button
      onClick={() => onSelect(doctor)}
      className={`w-full text-left p-4 rounded-xl border transition-all hover:shadow-md ${
        selected
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
          : 'border-gray-200 bg-white hover:border-blue-300'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {doctor.profile_photo ? (
            <img
              src={doctor.profile_photo}
              alt={doctor.full_name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center">
              <User className="w-6 h-6 text-teal-600" />
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-gray-900 text-sm truncate">{doctor.full_name}</span>
            {doctor.is_verified && (
              <BadgeCheck className="w-4 h-4 text-blue-500 flex-shrink-0" />
            )}
          </div>
          {doctor.specialty && (
            <div className="text-xs text-teal-600 font-medium mt-0.5">{doctor.specialty}</div>
          )}
          {doctor.headline && (
            <div className="text-xs text-gray-500 mt-1 line-clamp-1">{doctor.headline}</div>
          )}
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
            {doctor.institution && (
              <span className="flex items-center gap-1">
                <Building2 className="w-3 h-3" />
                {doctor.institution}
              </span>
            )}
            {doctor.city && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {doctor.city}
              </span>
            )}
          </div>
        </div>

        {/* Status */}
        <div className="flex-shrink-0">
          <span
            className={`text-xs px-2 py-1 rounded-full ${
              doctor.is_accepting_patients
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-500'
            }`}
          >
            {doctor.is_accepting_patients ? 'Uygun' : 'Musait Degil'}
          </span>
        </div>
      </div>
    </button>
  );
}
