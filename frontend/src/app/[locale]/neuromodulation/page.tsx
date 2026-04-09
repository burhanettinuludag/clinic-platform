'use client';

import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Brain, Zap, Radio, Sun, ChevronRight, BookOpen, CheckCircle, AlertCircle, FlaskConical, Award, ExternalLink } from 'lucide-react';

// ─── Types ───
interface TOCItem {
  id: string;
  label: string;
  level: number;
}

// ─── Evidence Badge Component ───
function EvidenceBadge({ level }: { level: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    'A': { bg: 'bg-green-100', text: 'text-green-800', label: 'Düzey A — Kesin Etkinlik' },
    'FDA': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'FDA Onaylı' },
    'B': { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Düzey B — Olası Etkinlik' },
    'C': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Düzey C — Muhtemel Etkinlik' },
    'RCT+': { bg: 'bg-teal-100', text: 'text-teal-800', label: 'RKÇ Pozitif' },
    'research': { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Araştırma Aşaması' },
    'promising': { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Umut Verici' },
    'limited': { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Sınırlı Kanıt' },
  };
  const c = config[level] || config['research'];
  return <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full ${c.bg} ${c.text}`}>{c.label}</span>;
}

// ─── TOC Sidebar ───
function TableOfContents({ items, activeId }: { items: TOCItem[]; activeId: string }) {
  return (
    <nav className="space-y-1">
      {items.map((item) => (
        <a
          key={item.id}
          href={`#${item.id}`}
          onClick={(e) => {
            e.preventDefault();
            document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }}
          className={`block text-sm py-1.5 border-l-2 transition-colors ${
            item.level === 2 ? 'pl-4' : 'pl-7'
          } ${
            activeId === item.id
              ? 'border-teal-600 text-teal-700 font-semibold bg-teal-50/50'
              : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'
          }`}
        >
          {item.label}
        </a>
      ))}
    </nav>
  );
}

// ─── Evidence Table ───
function EvidenceTable({ isTr }: { isTr: boolean }) {
  const rows = [
    { indication: isTr ? 'Depresyon' : 'Depression', rtms: 'A', tdcs: 'B', tps: 'research', pbm: 'limited' },
    { indication: isTr ? 'Nöropatik Ağrı' : 'Neuropathic Pain', rtms: 'A', tdcs: 'B', tps: 'research', pbm: 'research' },
    { indication: isTr ? 'Migren' : 'Migraine', rtms: 'B', tdcs: 'C', tps: '-', pbm: '-' },
    { indication: isTr ? 'Motor İnme' : 'Motor Stroke', rtms: 'A', tdcs: 'B', tps: '-', pbm: '-' },
    { indication: isTr ? 'Alzheimer' : 'Alzheimer\'s', rtms: 'C', tdcs: 'C', tps: 'RCT+', pbm: 'promising' },
    { indication: 'Parkinson', rtms: 'C', tdcs: 'C', tps: 'research', pbm: 'promising' },
    { indication: isTr ? 'Epilepsi' : 'Epilepsy', rtms: 'C', tdcs: 'C', tps: '-', pbm: '-' },
    { indication: isTr ? 'Sigara Bırakma' : 'Smoking Cessation', rtms: 'FDA', tdcs: 'C', tps: '-', pbm: '-' },
    { indication: isTr ? 'Alkol Bağımlılığı' : 'Alcohol Addiction', rtms: 'C', tdcs: 'C', tps: '-', pbm: '-' },
    { indication: 'OKB / OCD', rtms: 'FDA', tdcs: 'limited', tps: '-', pbm: '-' },
    { indication: isTr ? 'DEHB' : 'ADHD', rtms: 'C', tdcs: 'C', tps: '-', pbm: '-' },
    { indication: isTr ? 'Otizm' : 'Autism', rtms: 'limited', tdcs: 'limited', tps: '-', pbm: '-' },
    { indication: isTr ? 'Travmatik Beyin Hasarı' : 'TBI Cognitive', rtms: 'limited', tdcs: 'C', tps: '-', pbm: 'promising' },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="text-left py-3 px-3 font-semibold text-gray-700">{isTr ? 'Endikasyon' : 'Indication'}</th>
            <th className="text-center py-3 px-2 font-semibold text-gray-700">rTMS</th>
            <th className="text-center py-3 px-2 font-semibold text-gray-700">tDCS</th>
            <th className="text-center py-3 px-2 font-semibold text-gray-700">TPS</th>
            <th className="text-center py-3 px-2 font-semibold text-gray-700">PBM</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-gray-50/50' : ''}>
              <td className="py-2.5 px-3 font-medium text-gray-800">{row.indication}</td>
              {[row.rtms, row.tdcs, row.tps, row.pbm].map((val, j) => (
                <td key={j} className="text-center py-2.5 px-2">
                  {val === '-' ? <span className="text-gray-300">—</span> : <EvidenceBadge level={val} />}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Method Card ───
function MethodCard({ icon: Icon, title, description, color }: {
  icon: any; title: string; description: string; color: string;
}) {
  return (
    <div className={`rounded-xl border-2 ${color} p-5 hover:shadow-md transition-shadow`}>
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color.replace('border-', 'bg-').replace('-200', '-100')}`}>
          <Icon className="w-5 h-5 text-gray-700" />
        </div>
        <h3 className="font-bold text-gray-900">{title}</h3>
      </div>
      <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
    </div>
  );
}

// ─── Section Heading ───
function SectionHeading({ id, number, title, icon: Icon }: {
  id: string; number: string; title: string; icon: any;
}) {
  return (
    <div id={id} className="scroll-mt-24 flex items-center gap-3 mb-6 pt-8">
      <div className="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-sm shrink-0">
        {number}
      </div>
      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5 text-teal-600" />
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      </div>
    </div>
  );
}

// ─── Parameter List ───
function ParamList({ items }: { items: { label: string; value: string }[] }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 space-y-2">
      {items.map((item, i) => (
        <div key={i} className="flex gap-2 text-sm">
          <span className="font-semibold text-gray-700 whitespace-nowrap">{item.label}:</span>
          <span className="text-gray-600">{item.value}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Clinical Item ───
function ClinicalItem({ title, badge, children }: {
  title: string; badge?: string; children: React.ReactNode;
}) {
  return (
    <div className="border-l-4 border-teal-200 pl-4 py-2 mb-4">
      <div className="flex items-center gap-2 mb-1">
        <h4 className="font-semibold text-gray-800">{title}</h4>
        {badge && <EvidenceBadge level={badge} />}
      </div>
      <div className="text-sm text-gray-600 leading-relaxed">{children}</div>
    </div>
  );
}

// ─── Study Card ───
function StudyCard({ author, journal, description }: {
  author: string; journal: string; description: string;
}) {
  return (
    <div className="bg-white border rounded-lg p-4 mb-3">
      <div className="flex items-start gap-2">
        <FlaskConical className="w-4 h-4 text-teal-600 mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-medium text-gray-800">{author}</p>
          <p className="text-xs text-teal-600 mb-1">{journal}</p>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
      </div>
    </div>
  );
}

// ─── Reference Group ───
function ReferenceGroup({ title, refs }: { title: string; refs: string[] }) {
  return (
    <div className="mb-4">
      <h4 className="font-semibold text-gray-700 text-sm mb-2">{title}</h4>
      <ul className="space-y-1">
        {refs.map((ref, i) => (
          <li key={i} className="text-xs text-gray-500 leading-relaxed pl-4 relative before:content-['•'] before:absolute before:left-0 before:text-teal-400">
            {ref}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ═══════════════════════════════════════════════
// MAIN PAGE
// ═══════════════════════════════════════════════
export default function NeuromodulationPage() {
  const { locale } = useParams();
  const isTr = locale === 'tr';
  const [activeId, setActiveId] = useState('');

  const tocItems: TOCItem[] = isTr ? [
    { id: 'giris', label: 'Giriş', level: 1 },
    { id: 'rtms', label: '1. rTMS', level: 1 },
    { id: 'rtms-nedir', label: 'Nedir?', level: 2 },
    { id: 'rtms-parametreler', label: 'Parametreler', level: 2 },
    { id: 'rtms-klinik', label: 'Klinik Kullanım', level: 2 },
    { id: 'tes', label: '2. tES (tDCS/tACS/tRNS)', level: 1 },
    { id: 'tes-nedir', label: 'Nedir?', level: 2 },
    { id: 'tes-klinik', label: 'Klinik Kullanım', level: 2 },
    { id: 'tps', label: '3. TPS', level: 1 },
    { id: 'tps-nedir', label: 'Nedir?', level: 2 },
    { id: 'tps-alzheimer', label: 'Alzheimer\'da TPS', level: 2 },
    { id: 'tps-parkinson', label: 'Parkinson\'da TPS', level: 2 },
    { id: 'pbm', label: '4. Fotobiyomodülasyon', level: 1 },
    { id: 'pbm-nedir', label: 'Nedir?', level: 2 },
    { id: 'pbm-kanitlar', label: 'Klinik Kanıtlar', level: 2 },
    { id: 'endikasyonlar', label: '5. Endikasyonlar Tablosu', level: 1 },
    { id: 'kaynaklar', label: '6. Kaynaklar', level: 1 },
  ] : [
    { id: 'giris', label: 'Introduction', level: 1 },
    { id: 'rtms', label: '1. rTMS', level: 1 },
    { id: 'rtms-nedir', label: 'What is it?', level: 2 },
    { id: 'rtms-parametreler', label: 'Parameters', level: 2 },
    { id: 'rtms-klinik', label: 'Clinical Use', level: 2 },
    { id: 'tes', label: '2. tES (tDCS/tACS/tRNS)', level: 1 },
    { id: 'tes-nedir', label: 'What is it?', level: 2 },
    { id: 'tes-klinik', label: 'Clinical Use', level: 2 },
    { id: 'tps', label: '3. TPS', level: 1 },
    { id: 'tps-nedir', label: 'What is it?', level: 2 },
    { id: 'tps-alzheimer', label: 'TPS in Alzheimer\'s', level: 2 },
    { id: 'tps-parkinson', label: 'TPS in Parkinson\'s', level: 2 },
    { id: 'pbm', label: '4. Photobiomodulation', level: 1 },
    { id: 'pbm-nedir', label: 'What is it?', level: 2 },
    { id: 'pbm-kanitlar', label: 'Clinical Evidence', level: 2 },
    { id: 'endikasyonlar', label: '5. Evidence Table', level: 1 },
    { id: 'kaynaklar', label: '6. References', level: 1 },
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter(e => e.isIntersecting);
        if (visible.length > 0) {
          setActiveId(visible[0].target.id);
        }
      },
      { rootMargin: '-100px 0px -60% 0px', threshold: 0.1 }
    );

    tocItems.forEach(item => {
      const el = document.getElementById(item.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero */}
      <div className="bg-gradient-to-r from-teal-700 via-teal-600 to-cyan-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12 md:py-16">
          <div className="flex items-center gap-2 text-teal-200 text-sm mb-4">
            <BookOpen className="w-4 h-4" />
            <span>{isTr ? 'Eğitim İçeriği' : 'Educational Content'}</span>
            <ChevronRight className="w-3 h-3" />
            <span>{isTr ? 'Nöromodülasyon' : 'Neuromodulation'}</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3">
            {isTr ? 'Nöromodülasyon' : 'Neuromodulation'}
          </h1>
          <p className="text-lg md:text-xl text-teal-100 max-w-3xl leading-relaxed">
            {isTr
              ? 'Non-İnvaziv Beyin Stimülasyonu: Güncel Tedavi Yaklaşımları'
              : 'Non-Invasive Brain Stimulation: Current Treatment Approaches'}
          </p>
          <div className="flex flex-wrap gap-4 mt-6">
            {[
              { icon: Zap, label: 'rTMS' },
              { icon: Radio, label: 'tES' },
              { icon: Brain, label: 'TPS' },
              { icon: Sun, label: 'PBM' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2 bg-white/10 rounded-full px-4 py-1.5 text-sm">
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-teal-200 mt-6">
            {isTr ? 'Son güncelleme: Mart 2026 • Prof. Dr. Burhanettin Uludağ' : 'Last updated: March 2026 • Prof. Dr. Burhanettin Uludağ'}
          </p>
        </div>
      </div>

      {/* Layout: TOC + Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex gap-8">
          {/* Sticky TOC Sidebar */}
          <aside className="hidden lg:block w-64 shrink-0">
            <div className="sticky top-24">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                {isTr ? 'İçindekiler' : 'Contents'}
              </h3>
              <TableOfContents items={tocItems} activeId={activeId} />
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1 min-w-0 max-w-4xl">

            {/* ─── GİRİŞ ─── */}
            <section id="giris" className="scroll-mt-24 mb-8">
              <div className="bg-teal-50 border border-teal-200 rounded-xl p-6">
                <p className="text-gray-700 leading-relaxed">
                  {isTr
                    ? 'Nöromodülasyon, sinir sistemi aktivitesinin elektriksel, manyetik, ultrasonik veya optik enerji ile hedefli olarak değiştirilmesidir. Son yıllarda non-invaziv beyin stimülasyon yöntemleri, nöropsikiyatrik ve nörolojik hastalıkların tedavisinde giderek artan kanıt düzeyiyle klinik pratikte yerini almaktadır.'
                    : 'Neuromodulation is the targeted alteration of nervous system activity using electrical, magnetic, ultrasonic, or optical energy. In recent years, non-invasive brain stimulation methods have increasingly established their place in clinical practice for treating neuropsychiatric and neurological diseases.'}
                </p>
                <p className="text-gray-700 leading-relaxed mt-3">
                  {isTr
                    ? 'Bu sayfada dört ana nöromodülasyon yöntemini, kanıt düzeylerini ve klinik kullanım alanlarını güncel literatür eşliğinde bulabilirsiniz.'
                    : 'On this page, you can find the four main neuromodulation methods, their evidence levels, and clinical applications alongside current literature.'}
                </p>
              </div>

              {/* 4 Method Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
                <MethodCard
                  icon={Zap}
                  title={isTr ? 'rTMS — Manyetik Stimülasyon' : 'rTMS — Magnetic Stimulation'}
                  description={isTr
                    ? 'Tekrarlayan manyetik pulslarla kortikal uyarılabilirliği modüle eder. Depresyon ve ağrıda FDA onaylı.'
                    : 'Modulates cortical excitability with repetitive magnetic pulses. FDA-approved for depression and pain.'}
                  color="border-blue-200"
                />
                <MethodCard
                  icon={Radio}
                  title={isTr ? 'tES — Elektrik Stimülasyonu' : 'tES — Electrical Stimulation'}
                  description={isTr
                    ? 'Düşük şiddetli elektrik akımı ile kortikal aktiviteyi değiştirir. Taşınabilir ve evde uygulanabilir.'
                    : 'Alters cortical activity with low-intensity electrical current. Portable and home-applicable.'}
                  color="border-yellow-200"
                />
                <MethodCard
                  icon={Brain}
                  title={isTr ? 'TPS — Puls Stimülasyonu' : 'TPS — Pulse Stimulation'}
                  description={isTr
                    ? 'Ultrasonik şok dalgaları ile derin beyin stimülasyonu. Alzheimer tedavisinde CE onaylı.'
                    : 'Deep brain stimulation with ultrasonic shock waves. CE-approved for Alzheimer treatment.'}
                  color="border-teal-200"
                />
                <MethodCard
                  icon={Sun}
                  title={isTr ? 'PBM — Fotobiyomodülasyon' : 'PBM — Photobiomodulation'}
                  description={isTr
                    ? 'Kırmızı ve yakın kızılötesi ışık ile mitokondriyal fonksiyonu artırır. Nörodejenerasyonda umut verici.'
                    : 'Enhances mitochondrial function with red and near-infrared light. Promising for neurodegeneration.'}
                  color="border-orange-200"
                />
              </div>
            </section>

            {/* ═══════════════════════════════════════════ */}
            {/* BÖLÜM 1: rTMS */}
            {/* ═══════════════════════════════════════════ */}
            <SectionHeading id="rtms" number="1" title={isTr ? 'Tekrarlayıcı Transkraniyal Manyetik Stimülasyon (rTMS)' : 'Repetitive Transcranial Magnetic Stimulation (rTMS)'} icon={Zap} />

            <div id="rtms-nedir" className="scroll-mt-24 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">{isTr ? 'Nedir?' : 'What is it?'}</h3>
              <p className="text-gray-600 leading-relaxed mb-3">
                {isTr
                  ? 'rTMS, bir koil aracılığıyla kafatası üzerinden uygulanan değişken manyetik alanın beyin korteksinde elektrik akımı indüklemesi prensibine dayanır. Tekrarlanan pulslar korteks uyarılabilirliğini stimülasyon süresinin ötesinde kalıcı olarak modüle eder. Bu etki, uzun süreli potansiyalizasyon (LTP) ve uzun süreli depresyon (LTD) benzeri sinaptik plastisite mekanizmalarıyla açıklanmaktadır.'
                  : 'rTMS is based on the principle of inducing electrical current in the brain cortex through a variable magnetic field applied via a coil placed on the skull. Repeated pulses permanently modulate cortical excitability beyond the stimulation period, explained by long-term potentiation (LTP) and long-term depression (LTD)-like synaptic plasticity mechanisms.'}
              </p>
            </div>

            <div id="rtms-parametreler" className="scroll-mt-24 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">{isTr ? 'Temel Parametreler' : 'Key Parameters'}</h3>
              <div className="space-y-3">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400 mt-1.5 shrink-0" />
                      <div>
                        <span className="font-semibold text-gray-700">{isTr ? 'Düşük frekanslı (≤1 Hz):' : 'Low frequency (≤1 Hz):'}</span>{' '}
                        <span className="text-gray-600">{isTr ? 'İnhibitör etki — kortikal uyarılabilirliği azaltır' : 'Inhibitory effect — reduces cortical excitability'}</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 rounded-full bg-red-400 mt-1.5 shrink-0" />
                      <div>
                        <span className="font-semibold text-gray-700">{isTr ? 'Yüksek frekanslı (≥5 Hz):' : 'High frequency (≥5 Hz):'}</span>{' '}
                        <span className="text-gray-600">{isTr ? 'Eksitatör etki — kortikal uyarılabilirliği artırır' : 'Excitatory effect — increases cortical excitability'}</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 rounded-full bg-purple-400 mt-1.5 shrink-0" />
                      <div>
                        <span className="font-semibold text-gray-700">Theta Burst (TBS):</span>{' '}
                        <span className="text-gray-600">{isTr ? 'iTBS eksitatör, cTBS inhibitör' : 'iTBS excitatory, cTBS inhibitory'}</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 rounded-full bg-gray-400 mt-1.5 shrink-0" />
                      <div>
                        <span className="font-semibold text-gray-700">{isTr ? 'Koil tipleri:' : 'Coil types:'}</span>{' '}
                        <span className="text-gray-600">{isTr ? 'Figure-of-8 (fokal), dairesel (yaygın), H-koil (derin)' : 'Figure-of-8 (focal), circular (widespread), H-coil (deep)'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div id="rtms-klinik" className="scroll-mt-24 mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">{isTr ? 'Klinik Kullanım Alanları' : 'Clinical Applications'}</h3>

              <ClinicalItem title={isTr ? 'Majör Depresif Bozukluk' : 'Major Depressive Disorder'} badge="A">
                <p>{isTr
                  ? 'rTMS, tedaviye dirençli depresyonda en güçlü kanıt düzeyine sahip nöromodülasyon uygulamasıdır. Sol DLPFC üzerine yüksek frekanslı (10–20 Hz) rTMS veya iTBS, 2008\'den bu yana FDA onayına sahiptir.'
                  : 'rTMS has the strongest evidence level among neuromodulation applications for treatment-resistant depression. High-frequency (10-20 Hz) rTMS or iTBS over left DLPFC has been FDA-approved since 2008.'}</p>
                <p className="mt-2 font-medium text-teal-700">{isTr
                  ? 'Stanford SAINT protokolü: 5 gün süreyle günde 10 seans iTBS ile tedaviye dirençli depresyonda %79 remisyon oranı bildirilmiştir.'
                  : 'Stanford SAINT protocol: 10 sessions of iTBS per day for 5 days reported 79% remission rate in treatment-resistant depression.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Nöropatik Ağrı' : 'Neuropathic Pain'} badge="A">
                <p>{isTr
                  ? 'Primer motor korteks (M1) üzerine yüksek frekanslı (10–20 Hz) rTMS, kronik nöropatik ağrı tedavisinde kesin etkinlik düzeyine ulaşmıştır. Tekrarlayan M1-rTMS seansları 6 aya kadar süren analjezik etki sağlar. Stimülasyon genellikle motor eşiğin %80–90\'ında, 1500–3000 puls ile uygulanır.'
                  : 'High-frequency (10-20 Hz) rTMS over primary motor cortex (M1) has reached definite efficacy level for chronic neuropathic pain. Repeated M1-rTMS sessions provide analgesic effects lasting up to 6 months. Stimulation is typically applied at 80-90% motor threshold with 1500-3000 pulses.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Migren' : 'Migraine'} badge="B">
                <p>{isTr
                  ? 'DLPFC üzerine rTMS, migrenin akut tedavisi ve profilaksisinde orta-büyük etki boyutu göstermiştir. Tek puls TMS (sTMS) ile migren aurasının akut tedavisi FDA onayına sahiptir (SpringTMS cihazı).'
                  : 'rTMS over DLPFC has shown medium-to-large effect sizes for acute treatment and prophylaxis of migraine. Single-pulse TMS for acute treatment of migraine aura is FDA-approved (SpringTMS device).'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Motor İnme Rehabilitasyonu' : 'Motor Stroke Rehabilitation'} badge="A">
                <p>{isTr
                  ? 'Etkilenen hemisfer üzerine eksitatör veya sağlam hemisfer üzerine inhibitör rTMS, inme sonrası motor iyileşmede kesin etkinlik düzeyine sahiptir.'
                  : 'Excitatory rTMS over the affected hemisphere or inhibitory rTMS over the intact hemisphere has definite efficacy for post-stroke motor recovery.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Bağımlılık (Sigara ve Alkol)' : 'Addiction (Smoking & Alcohol)'} badge="FDA">
                <p>{isTr
                  ? 'Derin TMS (H-koil) ile bilateral DLPFC ve insula stimülasyonu, sigara bırakmada 2020\'den bu yana FDA onayına sahiptir (BrainsWay sistemi).'
                  : 'Deep TMS (H-coil) with bilateral DLPFC and insula stimulation has been FDA-approved for smoking cessation since 2020 (BrainsWay system).'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'OKB (Obsesif Kompulsif Bozukluk)' : 'OCD (Obsessive Compulsive Disorder)'} badge="FDA">
                <p>{isTr
                  ? 'Derin TMS ile medial prefrontal korteks ve anterior singulat korteks stimülasyonu, OKB tedavisinde 2018\'de FDA onayı almıştır.'
                  : 'Deep TMS with medial prefrontal cortex and anterior cingulate cortex stimulation received FDA approval for OCD in 2018.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Epilepsi' : 'Epilepsy'} badge="C">
                <p>{isTr
                  ? 'Epileptik odak üzerine düşük frekanslı (inhibitör) rTMS, fokal epilepsilerde nöbet sıklığını azaltmada olası etkinlik düzeyinde kanıt sunmaktadır.'
                  : 'Low-frequency (inhibitory) rTMS over the epileptic focus provides possible efficacy-level evidence for reducing seizure frequency in focal epilepsies.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Alzheimer ve Hafif Kognitif Bozukluk' : 'Alzheimer\'s and Mild Cognitive Impairment'} badge="C">
                <p>{isTr
                  ? 'Sol DLPFC veya bilateral parietal korteks üzerine yüksek frekanslı rTMS, Alzheimer hastalarında kognitif performansta iyileşme göstermiştir.'
                  : 'High-frequency rTMS over left DLPFC or bilateral parietal cortex has shown improvement in cognitive performance in Alzheimer patients.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'DEHB' : 'ADHD'} badge="C">
                <p>{isTr
                  ? 'Sağ DLPFC üzerine yüksek frekanslı rTMS, dikkat ve dürtüsellik semptomlarında iyileşme bildirmiştir. Büyük ölçekli RKÇ\'ler beklenmektedir.'
                  : 'High-frequency rTMS over right DLPFC has reported improvement in attention and impulsivity symptoms. Large-scale RCTs are awaited.'}</p>
              </ClinicalItem>
            </div>

            {/* ═══════════════════════════════════════════ */}
            {/* BÖLÜM 2: tES */}
            {/* ═══════════════════════════════════════════ */}
            <SectionHeading id="tes" number="2" title={isTr ? 'Transkraniyal Elektrik Stimülasyonu (tES)' : 'Transcranial Electrical Stimulation (tES)'} icon={Radio} />

            <div id="tes-nedir" className="scroll-mt-24 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">{isTr ? 'Nedir?' : 'What is it?'}</h3>
              <p className="text-gray-600 leading-relaxed mb-4">
                {isTr
                  ? 'Transkraniyal elektrik stimülasyonu, kafatası üzerinden sabit veya değişken düşük şiddetli elektrik akımı uygulayarak kortikal uyarılabilirliği modüle eder.'
                  : 'Transcranial electrical stimulation modulates cortical excitability by applying steady or alternating low-intensity electrical current through the skull.'}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                {[
                  {
                    title: 'tDCS',
                    desc: isTr ? 'Sabit doğru akım (1–2 mA). Anodal: uyarılabilirlik ↑, Katodal: ↓' : 'Steady direct current (1-2 mA). Anodal: excitability ↑, Cathodal: ↓',
                    color: 'bg-yellow-50 border-yellow-200',
                  },
                  {
                    title: 'tACS',
                    desc: isTr ? 'Sinüzoidal alternan akım. Spesifik beyin osilasyonlarını hedefler.' : 'Sinusoidal alternating current. Targets specific brain oscillations.',
                    color: 'bg-orange-50 border-orange-200',
                  },
                  {
                    title: 'tRNS',
                    desc: isTr ? 'Rastgele gürültü akımı. Stokastik rezonans ile kortikal uyarılabilirliği artırır.' : 'Random noise current. Increases cortical excitability via stochastic resonance.',
                    color: 'bg-red-50 border-red-200',
                  },
                ].map((item) => (
                  <div key={item.title} className={`rounded-lg border p-4 ${item.color}`}>
                    <h4 className="font-bold text-gray-800 mb-1">{item.title}</h4>
                    <p className="text-xs text-gray-600">{item.desc}</p>
                  </div>
                ))}
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 shrink-0" />
                  <p className="text-sm text-gray-700">
                    {isTr
                      ? 'Avantajları: Düşük maliyet, taşınabilirlik, evde uygulama potansiyeli ve minimal yan etkiler (en sık: hafif karıncalanma ve kızarıklık).'
                      : 'Advantages: Low cost, portability, home application potential, and minimal side effects (most common: mild tingling and redness).'}
                  </p>
                </div>
              </div>
            </div>

            <div id="tes-klinik" className="scroll-mt-24 mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">{isTr ? 'Klinik Kullanım Alanları' : 'Clinical Applications'}</h3>

              <ClinicalItem title={isTr ? 'Depresyon' : 'Depression'} badge="B">
                <p>{isTr
                  ? 'Sol DLPFC üzerine anodal tDCS, majör depresif bozuklukta olası etkinlik düzeyinde kanıt sunmaktadır. Ev tabanlı uzaktan tDCS uygulamasının etkili olduğu gösterilmiştir.'
                  : 'Anodal tDCS over left DLPFC provides probable efficacy-level evidence in major depressive disorder. Home-based remote tDCS has been shown effective.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Nöropatik Ağrı ve Fibromiyalji' : 'Neuropathic Pain & Fibromyalgia'} badge="B">
                <p>{isTr
                  ? 'M1 üzerine anodal tDCS, kronik ağrı ve fibromiyaljide analjezik etki göstermiştir.'
                  : 'Anodal tDCS over M1 has shown analgesic effects in chronic pain and fibromyalgia.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Epilepsi' : 'Epilepsy'} badge="C">
                <p>{isTr
                  ? 'Epileptik odak üzerine katodal tDCS, kortikal uyarılabilirliği azaltarak nöbet sıklığında azalma sağlayabilir.'
                  : 'Cathodal tDCS over the epileptic focus may reduce seizure frequency by decreasing cortical excitability.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Bağımlılık' : 'Addiction'} badge="C">
                <p>{isTr
                  ? 'DLPFC üzerine anodal tDCS, alkol, nikotin ve madde bağımlılığında craving azalması sağlamıştır.'
                  : 'Anodal tDCS over DLPFC has reduced craving in alcohol, nicotine, and substance addiction.'}</p>
              </ClinicalItem>
            </div>

            {/* ═══════════════════════════════════════════ */}
            {/* BÖLÜM 3: TPS */}
            {/* ═══════════════════════════════════════════ */}
            <SectionHeading id="tps" number="3" title={isTr ? 'Transkraniyal Puls Stimülasyonu (TPS)' : 'Transcranial Pulse Stimulation (TPS)'} icon={Brain} />

            <div id="tps-nedir" className="scroll-mt-24 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">{isTr ? 'Nedir?' : 'What is it?'}</h3>
              <p className="text-gray-600 leading-relaxed mb-4">
                {isTr
                  ? 'TPS, odaklanmış kısa ultrasonik pulsların (şok dalgalarının) kafatası üzerinden beyin dokusuna non-invaziv olarak uygulanmasıdır. 2018 yılında Alzheimer hastalığı tedavisi için CE onayı almıştır (Neurolith cihazı, Storz Medical). Diğer yöntemlerden farklı olarak derin beyin yapılarına ulaşabilme kapasitesine sahiptir.'
                  : 'TPS is the non-invasive application of focused short ultrasonic pulses (shock waves) to brain tissue through the skull. It received CE approval for Alzheimer disease treatment in 2018 (Neurolith device, Storz Medical). Unlike other methods, it has the capacity to reach deep brain structures.'}
              </p>

              <ParamList items={isTr ? [
                { label: 'Cihaz', value: 'Neurolith (Storz Medical AG)' },
                { label: 'Puls parametreleri', value: '0.20–0.25 mJ/mm², 4–5 Hz frekans, 3 μs puls süresi' },
                { label: 'Seans başına puls', value: '6000' },
                { label: 'Protokol', value: '6 seans / 2 hafta (gün aşırı) + aylık idame seansları' },
                { label: 'Nöronavigasyon', value: 'Bireysel 3D T1 MRG taraması ile hedef belirleme' },
                { label: 'Hedefler', value: 'Bilateral frontal, lateral parietal, temporal korteks, preküneus' },
              ] : [
                { label: 'Device', value: 'Neurolith (Storz Medical AG)' },
                { label: 'Pulse parameters', value: '0.20–0.25 mJ/mm², 4–5 Hz frequency, 3 μs pulse duration' },
                { label: 'Pulses per session', value: '6000' },
                { label: 'Protocol', value: '6 sessions / 2 weeks (every other day) + monthly maintenance' },
                { label: 'Neuronavigation', value: 'Individual 3D T1 MRI scan for target planning' },
                { label: 'Targets', value: 'Bilateral frontal, lateral parietal, temporal cortex, precuneus' },
              ]} />
            </div>

            <div id="tps-alzheimer" className="scroll-mt-24 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">{isTr ? 'Alzheimer Hastalığında TPS' : 'TPS in Alzheimer\'s Disease'}</h3>

              <StudyCard
                author="Matt ve ark. (2025)"
                journal="JAMA Network Open"
                description={isTr
                  ? '60 Alzheimer hastasında randomize, çift kör, sham kontrollü çapraz çalışma. Verum TPS, genç hasta alt grubunda kognitif skorlarda anlamlı iyileşme sağlamıştır. fMRG\'de bellek ilişkili beyin aktivasyonunda artış gösterilmiştir.'
                  : '60 Alzheimer patients in a randomized, double-blind, sham-controlled crossover study. Verum TPS showed significant cognitive improvement in younger patient subgroup. fMRI demonstrated increased memory-related brain activation.'}
              />
              <StudyCard
                author="Brain Stimulation (2024)"
                journal="Brain Stimulation"
                description={isTr
                  ? '10 hastada açık etiketli çalışma: TPS nöropsikiyatrik semptomları anlamlı düzeyde azaltmıştır (NPI skorunda 30 günde 23.9 puanlık düşüş, Cohen\'s d = 1.43).'
                  : '10 patients in open-label study: TPS significantly reduced neuropsychiatric symptoms (NPI score decrease of 23.9 points in 30 days, Cohen\'s d = 1.43).'}
              />
              <StudyCard
                author="Cont ve ark. (2022)"
                journal="Frontiers in Neurology"
                description={isTr
                  ? '101 nörodejeneratif hastalıkta TPS gerçek dünya verisi. Hastaların %80\'inden fazlasında yan etki bildirilmemiştir.'
                  : '101 neurodegenerative disease patients real-world data. No side effects reported in over 80% of patients.'}
              />
              <StudyCard
                author="Wojtecki ve ark. (2025)"
                journal="GeroScience"
                description={isTr
                  ? 'TPS sonrası EEG bazlı osilasyon ağ aktivitesinde değişiklikler — fonksiyonel bağlantıda artış ve plastik reorganizasyon bulguları.'
                  : 'Post-TPS changes in EEG-based oscillation network activity — increased functional connectivity and plastic reorganization findings.'}
              />
              <StudyCard
                author="Brain Sciences (2025)"
                journal="Brain Sciences"
                description={isTr
                  ? '10 Alzheimer hastasında 1 yıllık izlem. Bellek, konuşma, oryantasyon ve depresif semptomlarda uzun süreli olumlu etkiler.'
                  : '10 Alzheimer patients with 1-year follow-up. Long-term positive effects on memory, speech, orientation, and depressive symptoms.'}
              />
            </div>

            <div id="tps-parkinson" className="scroll-mt-24 mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">{isTr ? 'Parkinson Hastalığında TPS' : 'TPS in Parkinson\'s Disease'}</h3>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <p className="text-sm text-gray-700">
                  {isTr
                    ? 'TPS\'in Parkinson hastalığındaki güvenliği değerlendirilmiş ve herhangi bir yan etki gözlenmemiştir (Alon ve ark., 2012). Yürüme ve denge üzerine akut etkiler bildirilmiştir. Bu alandaki klinik çalışmalar devam etmektedir.'
                    : 'The safety of TPS in Parkinson\'s disease has been evaluated with no side effects observed (Alon et al., 2012). Acute effects on gait and balance have been reported. Clinical studies in this area are ongoing.'}
                </p>
              </div>

              <h4 className="text-sm font-semibold text-gray-700 mt-4 mb-2">{isTr ? 'Diğer Potansiyel Kullanım Alanları' : 'Other Potential Applications'}</h4>
              <div className="flex flex-wrap gap-2">
                {(isTr
                  ? ['Vasküler demans', 'Travmatik beyin hasarı', 'Depresyon', 'Serebral palsi', 'Kronik ağrı sendromları']
                  : ['Vascular dementia', 'Traumatic brain injury', 'Depression', 'Cerebral palsy', 'Chronic pain syndromes']
                ).map((item) => (
                  <span key={item} className="inline-flex items-center px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">{item}</span>
                ))}
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">{isTr ? 'Güvenlik' : 'Safety'}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {isTr
                        ? 'TPS genel olarak iyi tolere edilmektedir. Bildirilen yan etkiler ağrısız basınç hissi, hafif baş ağrısı ve geçici uyuşukluk olup tümü reversibldir. Hastaların %60\'ından fazlası herhangi bir yan etki bildirmemiştir.'
                        : 'TPS is generally well tolerated. Reported side effects include painless pressure sensation, mild headache, and transient numbness, all reversible. Over 60% of patients reported no side effects.'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* ═══════════════════════════════════════════ */}
            {/* BÖLÜM 4: PBM */}
            {/* ═══════════════════════════════════════════ */}
            <SectionHeading id="pbm" number="4" title={isTr ? 'Fotobiyomodülasyon (PBM)' : 'Photobiomodulation (PBM)'} icon={Sun} />

            <div id="pbm-nedir" className="scroll-mt-24 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">{isTr ? 'Nedir?' : 'What is it?'}</h3>
              <p className="text-gray-600 leading-relaxed mb-4">
                {isTr
                  ? 'Transkraniyal fotobiyomodülasyon (tPBM), kırmızı (600–670 nm) veya yakın kızılötesi (800–1100 nm) düşük yoğunluklu ışığın kafatası üzerinden beyin dokusuna non-invaziv olarak uygulanmasıdır.'
                  : 'Transcranial photobiomodulation (tPBM) is the non-invasive application of low-intensity red (600-670 nm) or near-infrared (800-1100 nm) light to brain tissue through the skull.'}
              </p>

              <h4 className="text-sm font-semibold text-gray-700 mb-2">{isTr ? 'Etki Mekanizması' : 'Mechanism of Action'}</h4>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-700 mb-2">{isTr ? 'Temel hedef: Mitokondriyal sitokrom c oksidaz (Kompleks IV)' : 'Primary target: Mitochondrial cytochrome c oxidase (Complex IV)'}</p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {(isTr
                    ? ['ATP üretimini artırır', 'Reaktif oksijen türlerini modüle eder', 'Nitrik oksit salınımını düzenler', 'Serebral kan akımını artırır', 'Nörogenez ve sinaptogenezi destekler', 'Nöroinflamasyonu azaltır']
                    : ['Increases ATP production', 'Modulates reactive oxygen species', 'Regulates nitric oxide release', 'Increases cerebral blood flow', 'Supports neurogenesis and synaptogenesis', 'Reduces neuroinflammation']
                  ).map((item, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-gray-600">
                      <CheckCircle className="w-3 h-3 text-orange-500 mt-0.5 shrink-0" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <ParamList items={isTr ? [
                { label: 'Uygulama', value: 'Transkraniyal (LED/lazer) ve/veya intranazal' },
                { label: 'Dalga boyu', value: '810 nm ve 1064 nm (en sık kullanılan)' },
                { label: 'Tipik protokol', value: '20 dakika seans, haftada 3 kez, 12 hafta' },
              ] : [
                { label: 'Application', value: 'Transcranial (LED/laser) and/or intranasal' },
                { label: 'Wavelength', value: '810 nm and 1064 nm (most commonly used)' },
                { label: 'Typical protocol', value: '20-minute sessions, 3 times per week, 12 weeks' },
              ]} />
            </div>

            <div id="pbm-kanitlar" className="scroll-mt-24 mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">{isTr ? 'Klinik Kanıtlar' : 'Clinical Evidence'}</h3>

              <ClinicalItem title={isTr ? 'Alzheimer ve Hafif Kognitif Bozukluk' : 'Alzheimer\'s and Mild Cognitive Impairment'} badge="promising">
                <p>{isTr
                  ? '35 klinik çalışmanın sistematik derlemesinde, çalışmaların %82.9\'u tPBM sonrası kognitif işlevlerde olumlu iyileşme bildirmiştir. Preklinik çalışmalar amiloid plak yükünü azaltabildiğini, nöroinflamasyonu baskıladığını ve hipokampal nörogenezi desteklediğini göstermiştir.'
                  : 'In a systematic review of 35 clinical studies, 82.9% reported positive improvement in cognitive function after tPBM. Preclinical studies have shown reduction in amyloid plaque burden, suppression of neuroinflammation, and support for hippocampal neurogenesis.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Parkinson Hastalığı' : 'Parkinson\'s Disease'} badge="promising">
                <p>{isTr
                  ? 'Hayvan modellerinde tPBM, dopaminerjik nöron kaybını azaltmış ve motor performansı iyileştirmiştir. İnsan çalışmaları sınırlı olmakla birlikte olumlu yönde eğilim göstermektedir.'
                  : 'In animal models, tPBM has reduced dopaminergic neuron loss and improved motor performance. Human studies are limited but show positive trends.'}</p>
              </ClinicalItem>

              <ClinicalItem title={isTr ? 'Travmatik Beyin Hasarı' : 'Traumatic Brain Injury'} badge="promising">
                <p>{isTr
                  ? 'tPBM, travmatik beyin hasarı sonrası kognitif iyileşmede 7 çalışmanın %87.5\'inde olumlu sonuç bildirmiştir.'
                  : 'tPBM reported positive results in 87.5% of 7 studies for cognitive recovery after traumatic brain injury.'}</p>
              </ClinicalItem>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">{isTr ? 'Sınırlılıklar' : 'Limitations'}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {isTr
                        ? 'Transkraniyal penetrasyon PBM\'in temel sınırlılığıdır. Işık; saç, kafa derisi, kan, kafatası kemiği ve kemik iliğinden geçmek zorundadır. Derin beyin yapılarına ulaşan enerji miktarı sınırlıdır. Standart protokoller henüz belirlenmemiştir.'
                        : 'Transcranial penetration is the fundamental limitation of PBM. Light must pass through hair, scalp, blood, skull bone, and bone marrow. Energy reaching deep brain structures is limited. Standard protocols have not yet been established.'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* ═══════════════════════════════════════════ */}
            {/* BÖLÜM 5: ENDİKASYONLAR TABLOSU */}
            {/* ═══════════════════════════════════════════ */}
            <SectionHeading id="endikasyonlar" number="5" title={isTr ? 'Klinik Endikasyonlar ve Kanıt Düzeyleri' : 'Clinical Indications and Evidence Levels'} icon={Award} />

            <div className="mb-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">{isTr ? 'Kanıt Düzeyi Sınıflaması (Lefaucheur ve ark., 2020)' : 'Evidence Level Classification (Lefaucheur et al., 2020)'}</h3>
              <div className="flex flex-wrap gap-3 mb-6">
                <EvidenceBadge level="A" />
                <EvidenceBadge level="B" />
                <EvidenceBadge level="C" />
                <EvidenceBadge level="FDA" />
                <EvidenceBadge level="RCT+" />
                <EvidenceBadge level="promising" />
                <EvidenceBadge level="research" />
              </div>
            </div>

            <div className="bg-white border rounded-xl p-4 mb-6 overflow-hidden">
              <EvidenceTable isTr={isTr} />
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">{isTr ? 'rTMS FDA Onaylı Endikasyonlar (2026 itibarıyla)' : 'rTMS FDA-Approved Indications (as of 2026)'}</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600">
                {[
                  { year: '2008', label: isTr ? 'Majör depresif bozukluk' : 'Major depressive disorder' },
                  { year: '2018', label: isTr ? 'Obsesif kompulsif bozukluk (derin TMS)' : 'Obsessive compulsive disorder (deep TMS)' },
                  { year: '2020', label: isTr ? 'Sigara bırakma (derin TMS)' : 'Smoking cessation (deep TMS)' },
                  { year: '2021', label: isTr ? 'Anksiyöz depresyon' : 'Anxious depression' },
                  { year: '—', label: isTr ? 'Migren — tek puls (SpringTMS)' : 'Migraine — single pulse (SpringTMS)' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-xs font-mono text-blue-600 w-10">{item.year}</span>
                    <span>{item.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* ═══════════════════════════════════════════ */}
            {/* BÖLÜM 6: KAYNAKLAR */}
            {/* ═══════════════════════════════════════════ */}
            <SectionHeading id="kaynaklar" number="6" title={isTr ? 'Kaynaklar' : 'References'} icon={BookOpen} />

            <div className="bg-gray-50 rounded-xl p-6 mb-8">
              <ReferenceGroup
                title={isTr ? 'Kılavuzlar ve Temel Derleme Makaleler' : 'Guidelines and Key Review Articles'}
                refs={[
                  'Lefaucheur JP, et al. Evidence-based guidelines on rTMS: An update (2014–2018). Clin Neurophysiol. 2020;131:474-528.',
                  'Fregni F, et al. Evidence-based guidelines for tDCS in neurological and psychiatric disorders. Int J Neuropsychopharmacol. 2021;24:256-313.',
                  'Cole E, et al. Accelerated theta burst stimulation: safety, efficacy, and future advancements. Biol Psychiatry. 2024;95:523-535.',
                ]}
              />
              <ReferenceGroup
                title={isTr ? 'rTMS — Nöropatik Ağrı' : 'rTMS — Neuropathic Pain'}
                refs={[
                  'Attal N, Genin T. rTMS for chronic pain: State of the art and perspectives. Neuromodulation. 2025.',
                  'Thomas L, et al. Effects of multiple rTMS sessions on pain relief in chronic neuropathic pain. Eur J Pain. 2025;29:e4763.',
                  'Zhou J, et al. Revisiting the effects of rTMS over DLPFC on pain: An updated systematic review. Brain Stimul. 2024;17:928-937.',
                ]}
              />
              <ReferenceGroup
                title={isTr ? 'rTMS — Depresyon ve Bağımlılık' : 'rTMS — Depression and Addiction'}
                refs={[
                  'Cole EJ, et al. Stanford SAINT: A randomized, double-blind, sham-controlled trial. Am J Psychiatry. 2022;179:132-141.',
                  'Zangen A, et al. Transcranial magnetic stimulation for smoking cessation. JAMA. 2020.',
                ]}
              />
              <ReferenceGroup
                title={isTr ? 'TPS — Transkraniyal Puls Stimülasyonu' : 'TPS — Transcranial Pulse Stimulation'}
                refs={[
                  'Matt E, et al. Ultrasound neuromodulation with TPS in Alzheimer disease: A randomized clinical trial. JAMA Netw Open. 2025;8(2):e2459170.',
                  'Cont C, et al. Retrospective real-world pilot data on TPS in Alzheimer\'s. Front Neurol. 2022;13:948204.',
                  'TPS improves neuropsychiatric symptoms in Alzheimer\'s disease. Brain Stimul. 2024.',
                  'Wojtecki L, et al. Electrical brain networks before and after TPS in Alzheimer\'s. GeroScience. 2025;47:953-964.',
                  'Brain Sciences 2025: TPS long-term feasibility in Alzheimer\'s disease — 1 year follow-up.',
                ]}
              />
              <ReferenceGroup
                title={isTr ? 'Fotobiyomodülasyon' : 'Photobiomodulation'}
                refs={[
                  'Brain photobiomodulation: A potential treatment in Alzheimer\'s and Parkinson\'s diseases. JPAD. 2025.',
                  'Chan AS, et al. Can transcranial photobiomodulation improve cognitive function? Ageing Res Rev. 2022;83:101786.',
                  'Dole M, et al. Effects of transcranial photobiomodulation on brain activity in humans. Rev Neurosci. 2023;34:671-693.',
                  'Transcranial photobiomodulation for brain diseases: review. Neurophoton. 2024;11(1):010601.',
                ]}
              />
              <ReferenceGroup
                title={isTr ? 'Genel Nöromodülasyon Derlemeleri' : 'General Neuromodulation Reviews'}
                refs={[
                  'Koch G, et al. The emerging field of non-invasive brain stimulation in Alzheimer\'s. Brain. 2024;awae292.',
                  'TMS in the treatment of neurological diseases. Front Neurol. 2022;13:793253.',
                  'Beisteiner R, Lozano AM. Transcranial ultrasound innovations ready for broad clinical application. Adv Sci. 2020;7(23):2002026.',
                ]}
              />
            </div>

            {/* Disclaimer */}
            <div className="bg-gray-100 rounded-xl p-6 mb-8 text-sm text-gray-500">
              <p className="italic">
                {isTr
                  ? 'Bu sayfa eğitim amaçlıdır ve tıbbi tavsiye yerine geçmez. Nöromodülasyon tedavileri, uzman hekim değerlendirmesi ve bireysel endikasyon belirlenmesi sonrası uygulanmalıdır.'
                  : 'This page is for educational purposes and does not substitute medical advice. Neuromodulation treatments should be administered after specialist physician evaluation and individual indication assessment.'}
              </p>
              <p className="mt-2">
                {isTr
                  ? 'Son güncelleme: Mart 2026 • © Norosera Nöroloji Kliniği — Prof. Dr. Burhanettin Uludağ'
                  : 'Last updated: March 2026 • © Norosera Neurology Clinic — Prof. Dr. Burhanettin Uludağ'}
              </p>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
