'use client';

import { useParams } from 'next/navigation';
import { useLocale } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { Dna, Clock, Eye, ArrowLeft, BookOpen, User, Calendar, ChevronRight } from 'lucide-react';
import { useMSArticle, useMSArticles } from '@/hooks/useMSData';

function renderMarkdown(content: string) {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let inTable = false;
  let tableRows: string[][] = [];
  let tableHeaders: string[] = [];

  const flushTable = () => {
    if (tableHeaders.length > 0) {
      elements.push(
        <div key={`table-${elements.length}`} className="overflow-x-auto my-4">
          <table className="min-w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
            <thead className="bg-gray-50">
              <tr>
                {tableHeaders.map((h, i) => (
                  <th key={i} className="px-4 py-2 text-left font-semibold text-gray-700 border-b">{h.trim()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, ri) => (
                <tr key={ri} className={ri % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  {row.map((cell, ci) => (
                    <td key={ci} className="px-4 py-2 text-gray-600 border-b border-gray-100">{cell.trim()}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    tableHeaders = [];
    tableRows = [];
    inTable = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Table detection
    if (line.includes('|') && line.trim().startsWith('|')) {
      const cells = line.split('|').filter(c => c.trim() !== '');
      if (!inTable) {
        inTable = true;
        tableHeaders = cells;
        continue;
      }
      if (cells.every(c => c.trim().match(/^[-:]+$/))) continue; // separator row
      tableRows.push(cells);
      continue;
    } else if (inTable) {
      flushTable();
    }

    // Empty line
    if (line.trim() === '') {
      elements.push(<div key={i} className="h-3" />);
      continue;
    }

    // Headings
    if (line.startsWith('### ')) {
      elements.push(<h3 key={i} className="text-lg font-bold text-gray-900 mt-8 mb-3">{line.replace('### ', '')}</h3>);
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(<h2 key={i} className="text-2xl font-bold text-gray-900 mt-10 mb-4">{line.replace('## ', '')}</h2>);
      continue;
    }

    // Blockquote
    if (line.startsWith('> ')) {
      const text = line.replace('> ', '');
      const parts = text.split(/\*\*(.*?)\*\*/g);
      elements.push(
        <blockquote key={i} className="border-l-4 border-cyan-500 bg-cyan-50 px-4 py-3 my-4 rounded-r-lg text-sm text-cyan-800">
          {parts.map((part, pi) => pi % 2 === 1 ? <strong key={pi}>{part}</strong> : part)}
        </blockquote>
      );
      continue;
    }

    // List item
    if (line.match(/^[-*] /)) {
      const text = line.replace(/^[-*] /, '');
      const parts = text.split(/\*\*(.*?)\*\*/g);
      elements.push(
        <li key={i} className="text-gray-700 text-[15px] leading-relaxed ml-4 list-disc mb-1.5">
          {parts.map((part, pi) => pi % 2 === 1 ? <strong key={pi} className="text-gray-900">{part}</strong> : part)}
        </li>
      );
      continue;
    }

    // Numbered list
    if (line.match(/^\d+\. /)) {
      const text = line.replace(/^\d+\. /, '');
      const parts = text.split(/\*\*(.*?)\*\*/g);
      elements.push(
        <li key={i} className="text-gray-700 text-[15px] leading-relaxed ml-4 list-decimal mb-1.5">
          {parts.map((part, pi) => pi % 2 === 1 ? <strong key={pi} className="text-gray-900">{part}</strong> : part)}
        </li>
      );
      continue;
    }

    // Regular paragraph with bold
    const parts = line.split(/\*\*(.*?)\*\*/g);
    elements.push(
      <p key={i} className="text-gray-700 text-[15px] leading-relaxed mb-2">
        {parts.map((part, pi) => pi % 2 === 1 ? <strong key={pi} className="text-gray-900">{part}</strong> : part)}
      </p>
    );
  }

  if (inTable) flushTable();
  return elements;
}

export default function MSArticlePage() {
  const params = useParams();
  const locale = useLocale();
  const slug = params?.slug as string;

  const { data: article, isLoading } = useMSArticle(slug);
  const { data: relatedArticles = [] } = useMSArticles(
    article?.category?.slug
      ? { category__slug: article.category.slug }
      : undefined
  );

  const otherArticles = relatedArticles.filter(a => a.slug !== slug).slice(0, 3);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white">
        <div className="max-w-3xl mx-auto px-4 py-16">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/3" />
            <div className="h-10 bg-gray-200 rounded w-3/4" />
            <div className="h-4 bg-gray-100 rounded w-full" />
            <div className="h-4 bg-gray-100 rounded w-2/3" />
            <div className="h-64 bg-gray-100 rounded mt-8" />
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Dna className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            {locale === 'tr' ? 'Makale bulunamadi' : 'Article not found'}
          </h2>
          <Link href="/ms" className="text-cyan-600 hover:underline">
            {locale === 'tr' ? 'MS Rehberine Don' : 'Back to MS Guide'}
          </Link>
        </div>
      </div>
    );
  }

  const coverUrl = article.cover_image_url || article.cover_image || '';

  return (
    <div className="min-h-screen bg-white">
      {/* Cover Image */}
      {coverUrl && (
        <div className="relative w-full h-56 sm:h-72 md:h-80 overflow-hidden">
          <img
            src={coverUrl}
            alt={article.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-cyan-900/90 via-cyan-900/40 to-transparent" />
        </div>
      )}
      {/* Header */}
      <div className={`bg-gradient-to-br from-cyan-900 via-cyan-800 to-teal-900 text-white ${coverUrl ? '-mt-24 relative z-10' : ''}`}>
        <div className="max-w-3xl mx-auto px-4 py-12">
          <Link
            href="/ms"
            className="inline-flex items-center gap-1.5 text-cyan-300 hover:text-white transition-colors text-sm mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            {locale === 'tr' ? 'MS Rehberine Don' : 'Back to MS Guide'}
          </Link>

          <div className="flex items-center gap-2 mb-4 flex-wrap">
            {article.category && (
              <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-white/15 text-white">
                {article.category.name}
              </span>
            )}
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold mb-3 tracking-tight">{article.title}</h1>
          {article.subtitle && (
            <p className="text-lg text-cyan-200">{article.subtitle}</p>
          )}

          <div className="flex items-center gap-4 mt-6 text-sm text-cyan-300 flex-wrap">
            <span className="flex items-center gap-1.5">
              <User className="w-4 h-4" />
              {article.author_name}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              {article.reading_time_minutes} {locale === 'tr' ? 'dk okuma' : 'min read'}
            </span>
            <span className="flex items-center gap-1.5">
              <Eye className="w-4 h-4" />
              {article.view_count} {locale === 'tr' ? 'goruntulenme' : 'views'}
            </span>
            <span className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4" />
              {new Date(article.created_at).toLocaleDateString(locale === 'tr' ? 'tr-TR' : 'en-US')}
            </span>
          </div>
        </div>
      </div>

      {/* Content */}
      <article className="max-w-3xl mx-auto px-4 py-10">
        {article.summary && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 mb-8">
            <p className="text-gray-700 text-[15px] leading-relaxed italic">{article.summary}</p>
          </div>
        )}

        <div className="prose-custom">
          {article.content && renderMarkdown(article.content)}
        </div>

        {/* References */}
        {article.references && (
          <div className="mt-12 pt-8 border-t border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-gray-400" />
              {locale === 'tr' ? 'Kaynaklar' : 'References'}
            </h3>
            <ol className="space-y-2">
              {article.references.split('\n').filter(r => r.trim()).map((ref, i) => (
                <li key={i} className="text-sm text-gray-500 pl-4 border-l-2 border-gray-200">
                  {ref}
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-10 bg-amber-50 border border-amber-200 rounded-xl p-5">
          <p className="text-sm text-amber-800">
            <strong>{locale === 'tr' ? 'Uyari:' : 'Disclaimer:'}</strong>{' '}
            {locale === 'tr'
              ? 'Bu sayfadaki icerikler yalnizca bilgilendirme amaclidir ve tibbi tani veya tedavi yerine gecmez. Saglik sorunlariniz icin mutlaka bir noroloji uzmani ile gorusun.'
              : 'The content on this page is for informational purposes only and does not replace medical diagnosis or treatment. Always consult a neurologist for your health concerns.'}
          </p>
        </div>
      </article>

      {/* Related Articles */}
      {otherArticles.length > 0 && (
        <section className="bg-gray-50 border-t border-gray-200">
          <div className="max-w-3xl mx-auto px-4 py-12">
            <h3 className="text-xl font-bold text-gray-900 mb-6">
              {locale === 'tr' ? 'Ilgili Makaleler' : 'Related Articles'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {otherArticles.map(a => (
                <Link
                  key={a.id}
                  href={`/ms/${a.slug}`}
                  className="bg-white rounded-xl p-4 border border-gray-200 hover:border-cyan-300 hover:shadow-sm transition-all group"
                >
                  <h4 className="font-semibold text-sm text-gray-900 group-hover:text-cyan-700 transition-colors line-clamp-2 mb-2">
                    {a.title}
                  </h4>
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Clock className="w-3 h-3" />
                    {a.reading_time_minutes} dk
                    <ChevronRight className="w-3 h-3 ml-auto text-cyan-500" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
