'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';

const mockData = {
  fileName: 'customer_data.csv',
  rows: 1250,
  columns: [
    { name: 'customer_id', type: 'integer' },
    { name: 'name', type: 'string' },
    { name: 'email', type: 'string' },
    { name: 'age', type: 'integer' },
    { name: 'city', type: 'string' },
    { name: 'purchase_amount', type: 'float' },
    { name: 'signup_date', type: 'date' },
  ],
  preview: [
    { customer_id: 1, name: 'John Smith', email: 'john@email.com', age: 28, city: 'New York', purchase_amount: 150.50, signup_date: '2024-01-15' },
    { customer_id: 2, name: 'Sarah Johnson', email: 'sarah@email.com', age: 34, city: 'Los Angeles', purchase_amount: 220.00, signup_date: '2024-01-18' },
    { customer_id: 3, name: 'Mike Brown', email: null, age: 45, city: 'Chicago', purchase_amount: 89.99, signup_date: '2024-01-20' },
    { customer_id: 4, name: 'Emily Davis', email: 'emily@email.com', age: null, city: 'Houston', purchase_amount: 310.25, signup_date: '2024-01-22' },
    { customer_id: 5, name: 'David Wilson', email: 'david@email.com', age: 29, city: 'Phoenix', purchase_amount: 175.80, signup_date: '2024-01-25' },
    { customer_id: 6, name: 'Lisa Anderson', email: 'lisa@email.com', age: 52, city: 'Philadelphia', purchase_amount: 420.00, signup_date: '2024-01-28' },
    { customer_id: 7, name: 'James Taylor', email: 'james@email.com', age: 38, city: 'San Antonio', purchase_amount: 95.50, signup_date: '2024-02-01' },
    { customer_id: 8, name: 'Mary Martinez', email: null, age: 41, city: 'San Diego', purchase_amount: 260.75, signup_date: '2024-02-03' },
    { customer_id: 9, name: 'Robert Garcia', email: 'robert@email.com', age: 33, city: 'Dallas', purchase_amount: 185.00, signup_date: '2024-02-05' },
    { customer_id: 10, name: 'Jennifer Lee', email: 'jennifer@email.com', age: 27, city: 'San Jose', purchase_amount: 340.50, signup_date: '2024-02-08' },
  ]
};

export default function PreviewPage() {
  const router = useRouter();

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'integer':
        return 'bg-blue-100 text-blue-700';
      case 'float':
        return 'bg-green-100 text-green-700';
      case 'string':
        return 'bg-purple-100 text-purple-700';
      case 'date':
        return 'bg-orange-100 text-orange-700';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Dataset Preview</h1>
          <p className="text-slate-600">Review your dataset before analysis</p>
        </div>

        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">{mockData.fileName}</h2>
              <p className="text-sm text-slate-600 mt-1">
                {mockData.rows.toLocaleString()} rows × {mockData.columns.length} columns
              </p>
            </div>
            <Button
              onClick={() => router.push('/analysis')}
              className="bg-blue-500 hover:bg-blue-600"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Analyze Dataset
            </Button>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Column Types</h3>
            <div className="flex flex-wrap gap-2">
              {mockData.columns.map((col) => (
                <div key={col.name} className="flex items-center gap-2">
                  <span className="text-sm text-slate-700 font-medium">{col.name}</span>
                  <Badge className={getTypeColor(col.type)} variant="secondary">
                    {col.type}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b">
                  <tr>
                    {mockData.columns.map((col) => (
                      <th key={col.name} className="px-4 py-3 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider whitespace-nowrap">
                        {col.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {mockData.preview.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50">
                      {mockData.columns.map((col) => (
                        <td key={col.name} className="px-4 py-3 text-sm text-slate-700 whitespace-nowrap">
                          {row[col.name as keyof typeof row] !== null && row[col.name as keyof typeof row] !== undefined ? (
                            String(row[col.name as keyof typeof row])
                          ) : (
                            <span className="text-red-500 italic">null</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <p className="text-xs text-slate-500 mt-4">
            Showing first 10 rows of {mockData.rows.toLocaleString()}
          </p>
        </Card>
      </div>
    </DashboardLayout>
  );
}
