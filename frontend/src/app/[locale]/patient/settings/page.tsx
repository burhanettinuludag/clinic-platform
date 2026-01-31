"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { useConsents, useGrantConsent } from "@/hooks/useDoctorData";
import { Bell, Shield, Mail, Cookie } from "lucide-react";

interface ConsentItem {
  key: string;
  label: string;
  description: string;
  icon: React.ReactNode;
}

export default function PatientSettingsPage() {
  const t = useTranslations();
  const { data: consents, isLoading } = useConsents();
  const grantConsent = useGrantConsent();

  const [localConsents, setLocalConsents] = useState<Record<string, boolean>>({
    health_data: false,
    doctor_sharing: false,
    marketing: false,
    cookies: false,
  });

  useEffect(() => {
    if (consents && Array.isArray(consents)) {
      const consentMap: Record<string, boolean> = {};
      consents.forEach((consent: { consent_type: string; granted: boolean }) => {
        consentMap[consent.consent_type] = consent.granted;
      });
      setLocalConsents((prev) => ({ ...prev, ...consentMap }));
    }
  }, [consents]);

  const consentItems: ConsentItem[] = [
    {
      key: "health_data",
      label: "Saglik Verisi Isleme",
      description: "Saglik verilerinizin takip amacli islenmesine izin verin.",
      icon: <Shield className="w-5 h-5 text-blue-600" />,
    },
    {
      key: "doctor_sharing",
      label: "Hekim ile Paylasim",
      description: "Verilerinizin hekiminizle paylasilmasina izin verin.",
      icon: <Bell className="w-5 h-5 text-green-600" />,
    },
    {
      key: "marketing",
      label: "Pazarlama Iletisimi",
      description: "Promosyon ve bilgilendirme e-postalari alin.",
      icon: <Mail className="w-5 h-5 text-purple-600" />,
    },
    {
      key: "cookies",
      label: "Cerez Kullanimi",
      description: "Analitik cerezlerin kullanimina izin verin.",
      icon: <Cookie className="w-5 h-5 text-amber-600" />,
    },
  ];

  const handleToggle = (consentType: string) => {
    const newValue = !localConsents[consentType];
    setLocalConsents((prev) => ({ ...prev, [consentType]: newValue }));
    grantConsent.mutate({
      consent_type: consentType,
      granted: newValue,
      version: "1.0",
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Yukleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Ayarlar</h1>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Onay ve KVKK Tercihleri
          </h2>
          <p className="text-gray-500 text-sm mb-6">
            Kisisel verilerinizin islenmesine iliskin tercihlerinizi yonetin.
          </p>

          <div className="space-y-6">
            {consentItems.map((item) => (
              <div
                key={item.key}
                className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0"
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">{item.icon}</div>
                  <div>
                    <p className="font-medium text-gray-800">{item.label}</p>
                    <p className="text-sm text-gray-500">{item.description}</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={localConsents[item.key]}
                    onClick={() => handleToggle(item.key)}
                    className={`w-11 h-6 rounded-full transition-colors duration-200 ease-in-out ${
                      localConsents[item.key] ? "bg-blue-600" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`block w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200 ease-in-out ${
                        localConsents[item.key]
                          ? "translate-x-5"
                          : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </label>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
