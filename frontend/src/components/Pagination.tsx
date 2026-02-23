import React from 'react';

interface PaginationProps {
  page: number;
  pages: number;
  total: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ page, pages, total, onPageChange }) => {
  if (pages <= 1) return null;

  const getPageNumbers = () => {
    const nums: (number | '...')[] = [];
    if (pages <= 7) {
      for (let i = 1; i <= pages; i++) nums.push(i);
    } else {
      nums.push(1);
      if (page > 3) nums.push('...');
      for (let i = Math.max(2, page - 1); i <= Math.min(pages - 1, page + 1); i++) {
        nums.push(i);
      }
      if (page < pages - 2) nums.push('...');
      nums.push(pages);
    }
    return nums;
  };

  return (
    <div className="flex items-center justify-between mt-4">
      <p className="text-sm text-gray-600">
        Total: <span className="font-medium">{total}</span> items
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="px-3 py-1 text-sm rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          « Previous
        </button>
        {getPageNumbers().map((num, idx) =>
          num === '...' ? (
            <span key={`ellipsis-${idx}`} className="px-2 py-1 text-gray-400">
              …
            </span>
          ) : (
            <button
              key={num}
              onClick={() => onPageChange(num)}
              className={`px-3 py-1 text-sm rounded border ${
                num === page
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              {num}
            </button>
          )
        )}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === pages}
          className="px-3 py-1 text-sm rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Next »
        </button>
      </div>
    </div>
  );
};
