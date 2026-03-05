'use client';

import { Button } from '@/components/ui/button';
import { Upload, Sparkles, Database, Code as Code2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center mb-8">
            <div className="p-4 bg-blue-500 rounded-2xl">
              <Sparkles className="h-12 w-12 text-white" />
            </div>
          </div>

          <h1 className="text-5xl font-bold text-slate-900 mb-6">
            AI Data Cleaning Assistant
          </h1>

          <p className="text-xl text-slate-600 mb-12 max-w-2xl mx-auto">
            Upload your dataset and automatically detect data quality issues with AI.
            Get intelligent recommendations and ready-to-use cleaning code.
          </p>

          <Button
            onClick={() => router.push('/upload')}
            size="lg"
            className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-6 text-lg h-auto"
          >
            <Upload className="mr-2 h-5 w-5" />
            Upload Dataset
          </Button>

          <div className="grid md:grid-cols-3 gap-8 mt-20">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Smart Analysis</h3>
              <p className="text-slate-600 text-sm">
                Automatically detect missing values, duplicates, outliers, and data type issues
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Sparkles className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">AI Recommendations</h3>
              <p className="text-slate-600 text-sm">
                Get intelligent suggestions tailored to your specific data quality issues
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Code2 className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Ready-to-Use Code</h3>
              <p className="text-slate-600 text-sm">
                Generate production-ready Python code to clean your dataset instantly
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
