import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const alt = 'Norosera - Neurology Platform';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: 'linear-gradient(135deg, #f0fdfa 0%, #ffffff 50%, #eef2ff 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Inter, Arial, sans-serif',
        }}
      >
        {/* Top accent bar */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 6, background: 'linear-gradient(90deg, #0d9488, #6366f1)', display: 'flex' }} />

        {/* Logo circle */}
        <div
          style={{
            width: 100,
            height: 100,
            borderRadius: 50,
            background: 'linear-gradient(135deg, #0d9488, #0f766e)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 24,
            boxShadow: '0 20px 40px rgba(13,148,136,0.3)',
          }}
        >
          <span style={{ fontSize: 52, fontWeight: 800, color: 'white' }}>N</span>
        </div>

        {/* Title */}
        <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 16 }}>
          <span style={{ fontSize: 56, fontWeight: 800, color: '#0d9488' }}>noro</span>
          <span style={{ fontSize: 56, fontWeight: 800, color: '#1f2937' }}>sera</span>
        </div>

        {/* Subtitle */}
        <p style={{ fontSize: 24, color: '#6b7280', textAlign: 'center', maxWidth: 700, lineHeight: 1.4, margin: 0 }}>
          Neurology Platform for Migraine, Epilepsy & Dementia
        </p>

        {/* Trust badges */}
        <div style={{ display: 'flex', gap: 16, marginTop: 32 }}>
          {['KVKK Compliant', 'Doctor Approved', 'Data Encrypted'].map((badge) => (
            <div
              key={badge}
              style={{
                padding: '8px 16px',
                borderRadius: 20,
                background: 'rgba(13,148,136,0.1)',
                border: '1px solid rgba(13,148,136,0.2)',
                fontSize: 14,
                color: '#0d9488',
                fontWeight: 600,
                display: 'flex',
              }}
            >
              {badge}
            </div>
          ))}
        </div>

        {/* URL */}
        <p style={{ position: 'absolute', bottom: 24, fontSize: 16, color: '#9ca3af', margin: 0 }}>
          norosera.com
        </p>
      </div>
    ),
    { ...size }
  );
}
