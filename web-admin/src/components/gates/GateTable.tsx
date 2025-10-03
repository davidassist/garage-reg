import { useState, useMemo } from 'react'
import { 
  useReactTable, 
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type VisibilityState,
} from '@tanstack/react-table'
import { 
  ChevronDown, 
  ChevronUp, 
  MoreHorizontal, 
  Edit, 
  Eye, 
  Trash2,
  Settings,
  Search,
  Filter,
  Download,
  Plus,
} from 'lucide-react'
import { format } from 'date-fns'
import { hu } from 'date-fns/locale'

import { 
  Gate, 
  GateTypeLabels, 
  GateStatusLabels, 
  GateStatusColors,
} from '@/lib/types/gate'
import type { Gate as GateType } from '@/lib/types/gate'

interface GateTableProps {
  gates: Gate[]
  isLoading?: boolean
  onEdit: (gate: Gate) => void
  onView: (gate: Gate) => void
  onDelete: (gate: Gate) => void
  onCreateNew: () => void
}

export default function GateTable({ 
  gates, 
  isLoading = false, 
  onEdit, 
  onView, 
  onDelete,
  onCreateNew 
}: GateTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [globalFilter, setGlobalFilter] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  const columns = useMemo<ColumnDef<Gate>[]>(
    () => [
      {
        accessorKey: 'code',
        header: ({ column }) => (
          <button
            className="flex items-center space-x-2 hover:bg-gray-100 px-2 py-1 rounded"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            <span>Kód</span>
            {column.getIsSorted() === 'asc' ? (
              <ChevronUp className="h-4 w-4" />
            ) : column.getIsSorted() === 'desc' ? (
              <ChevronDown className="h-4 w-4" />
            ) : null}
          </button>
        ),
        cell: ({ row }) => (
          <div className="font-medium text-gray-900">
            {row.getValue('code')}
          </div>
        ),
      },
      {
        accessorKey: 'name',
        header: ({ column }) => (
          <button
            className="flex items-center space-x-2 hover:bg-gray-100 px-2 py-1 rounded"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            <span>Név</span>
            {column.getIsSorted() === 'asc' ? (
              <ChevronUp className="h-4 w-4" />
            ) : column.getIsSorted() === 'desc' ? (
              <ChevronDown className="h-4 w-4" />
            ) : null}
          </button>
        ),
        cell: ({ row }) => (
          <div className="text-gray-900">
            {row.getValue('name')}
          </div>
        ),
      },
      {
        accessorKey: 'type',
        header: 'Típus',
        cell: ({ row }) => {
          const type = row.getValue('type') as keyof typeof GateTypeLabels
          return (
            <div className="text-gray-600">
              {GateTypeLabels[type]}
            </div>
          )
        },
        filterFn: 'equals',
      },
      {
        accessorKey: 'status',
        header: 'Állapot',
        cell: ({ row }) => {
          const status = row.getValue('status') as keyof typeof GateStatusLabels
          const colorClasses = GateStatusColors[status]
          return (
            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full border ${colorClasses}`}>
              {GateStatusLabels[status]}
            </span>
          )
        },
        filterFn: 'equals',
      },
      {
        accessorKey: 'manufacturer',
        header: 'Gyártó',
        cell: ({ row }) => (
          <div className="text-gray-600">
            {row.getValue('manufacturer')}
          </div>
        ),
      },
      {
        accessorKey: 'serialNumber',
        header: 'Sorozatszám',
        cell: ({ row }) => (
          <div className="text-gray-600 font-mono text-sm">
            {row.getValue('serialNumber')}
          </div>
        ),
      },
      {
        accessorKey: 'location',
        header: 'Helyszín',
        cell: ({ row }) => (
          <div className="text-gray-600">
            {row.getValue('location') || '-'}
          </div>
        ),
      },
      {
        accessorKey: 'lastMaintenance',
        header: ({ column }) => (
          <button
            className="flex items-center space-x-2 hover:bg-gray-100 px-2 py-1 rounded"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            <span>Utolsó karbantartás</span>
            {column.getIsSorted() === 'asc' ? (
              <ChevronUp className="h-4 w-4" />
            ) : column.getIsSorted() === 'desc' ? (
              <ChevronDown className="h-4 w-4" />
            ) : null}
          </button>
        ),
        cell: ({ row }) => {
          const date = row.getValue('lastMaintenance') as string | null
          return (
            <div className="text-gray-600 text-sm">
              {date 
                ? format(new Date(date), 'yyyy. MM. dd.', { locale: hu })
                : '-'
              }
            </div>
          )
        },
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          const gate = row.original
          return (
            <div className="flex items-center justify-end space-x-2">
              <button
                onClick={() => onView(gate)}
                className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                title="Megtekintés"
              >
                <Eye className="h-4 w-4" />
              </button>
              <button
                onClick={() => onEdit(gate)}
                className="p-1 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded"
                title="Szerkesztés"
              >
                <Edit className="h-4 w-4" />
              </button>
              <button
                onClick={() => onDelete(gate)}
                className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                title="Törlés"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          )
        },
        enableSorting: false,
      },
    ],
    [onEdit, onView, onDelete]
  )

  const table = useReactTable({
    data: gates,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-4 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header with controls */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Kapuk</h2>
          <div className="flex items-center space-x-3">
            <button
              onClick={onCreateNew}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Plus className="h-4 w-4 mr-2" />
              Új kapu
            </button>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-md border ${
                showFilters 
                  ? 'bg-blue-50 border-blue-200 text-blue-600' 
                  : 'bg-white border-gray-300 text-gray-400 hover:text-gray-500'
              }`}
              title="Szűrők"
            >
              <Filter className="h-4 w-4" />
            </button>
            <button
              className="p-2 text-gray-400 hover:text-gray-500 border border-gray-300 rounded-md"
              title="Oszlopok"
            >
              <Settings className="h-4 w-4" />
            </button>
            <button
              className="p-2 text-gray-400 hover:text-gray-500 border border-gray-300 rounded-md"
              title="Export"
            >
              <Download className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        {/* Search bar */}
        <div className="mt-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Keresés kapuk között..."
              value={globalFilter ?? ''}
              onChange={(e) => setGlobalFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Típus
              </label>
              <select
                value={(table.getColumn('type')?.getFilterValue() as string) ?? ''}
                onChange={(e) =>
                  table.getColumn('type')?.setFilterValue(e.target.value || undefined)
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Minden típus</option>
                {Object.entries(GateTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Állapot
              </label>
              <select
                value={(table.getColumn('status')?.getFilterValue() as string) ?? ''}
                onChange={(e) =>
                  table.getColumn('status')?.setFilterValue(e.target.value || undefined)
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Minden állapot</option>
                {Object.entries(GateStatusLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map((row) => (
              <tr 
                key={row.id} 
                className="hover:bg-gray-50 transition-colors duration-150"
              >
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-6 py-4 whitespace-nowrap text-sm"
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty state */}
      {table.getRowModel().rows.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">Nincsenek kapuk</div>
          <p className="text-gray-400 mt-2">
            {globalFilter || columnFilters.length > 0
              ? 'Próbálja meg módosítani a szűrőket'
              : 'Kezdje el egy új kapu hozzáadásával'
            }
          </p>
        </div>
      )}

      {/* Pagination */}
      {table.getPageCount() > 1 && (
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Összesen {table.getFilteredRowModel().rows.length} kapu
              {table.getState().globalFilter && (
                <span className="ml-2 text-gray-500">
                  (szűrve {gates.length} közül)
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Előző
              </button>
              <span className="text-sm text-gray-700">
                {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
              </span>
              <button
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Következő
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}