'use client'

import { useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth/context'
import { withRequiredAuth } from '@/lib/auth/with-auth'
import Breadcrumbs, { createBreadcrumbs } from '@/components/layout/Breadcrumbs'
import { 
  Search,
  Users,
  Building2,
  Home,
  DoorOpen,
  Shield,
  Bug,
  FileText,
  Package,
  Clock,
  Filter,
  SortAsc,
  Grid,
  List,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchResult {
  id: string
  type: 'client' | 'site' | 'building' | 'gate' | 'inspection' | 'ticket' | 'workorder' | 'document' | 'inventory'
  title: string
  description: string
  url: string
  lastModified?: Date
  status?: string
  priority?: 'low' | 'medium' | 'high'
  tags?: string[]
}

const mockSearchResults: SearchResult[] = [
  {
    id: '1',
    type: 'client',
    title: 'ABC Logistics Kft.',
    description: 'Raktározási és logisztikai szolgáltatások',
    url: '/clients/1',
    lastModified: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'Aktív',
    tags: ['logisztika', 'raktár', 'szállítás']
  },
  {
    id: '2',
    type: 'site',
    title: 'Budapest Raktárközpont',
    description: 'Fő raktározási telephely Budapesten',
    url: '/sites/2',
    lastModified: new Date(Date.now() - 4 * 60 * 60 * 1000),
    status: 'Működik',
    tags: ['budapest', 'raktár', 'központ']
  },
  {
    id: '3',
    type: 'gate',
    title: 'Kapu A-003',
    description: 'Főbejárat - automatikus azonosítóval',
    url: '/gates/3',
    lastModified: new Date(Date.now() - 30 * 60 * 1000),
    status: 'Karbantartás szükséges',
    priority: 'medium',
    tags: ['főbejárat', 'automatikus', 'rfid']
  },
  {
    id: '4',
    type: 'inspection',
    title: 'Biztonsági ellenőrzés - Q1 2025',
    description: 'Negyedéves biztonsági felülvizsgálat',
    url: '/inspections/4',
    lastModified: new Date(Date.now() - 6 * 60 * 60 * 1000),
    status: 'Folyamatban',
    priority: 'high',
    tags: ['biztonság', 'negyedéves', 'felülvizsgálat']
  },
  {
    id: '5',
    type: 'ticket',
    title: 'Kapu szenzor hibája',
    description: 'A kapu mozgásérzékelője nem működik megfelelően',
    url: '/tickets/5',
    lastModified: new Date(Date.now() - 1 * 60 * 60 * 1000),
    status: 'Nyitott',
    priority: 'high',
    tags: ['szenzor', 'kapu', 'hiba']
  }
]

const typeIcons = {
  client: Users,
  site: Building2,
  building: Home,
  gate: DoorOpen,
  inspection: Shield,
  ticket: Bug,
  workorder: FileText,
  document: FileText,
  inventory: Package,
}

const typeLabels = {
  client: 'Ügyfél',
  site: 'Telephely',
  building: 'Épület',
  gate: 'Kapu',
  inspection: 'Ellenőrzés',
  ticket: 'Hibajegy',
  workorder: 'Munkalap',
  document: 'Dokumentum',
  inventory: 'Raktár',
}

const priorityColors = {
  low: 'text-green-600 bg-green-50 border-green-200',
  medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  high: 'text-red-600 bg-red-50 border-red-200',
}

function SearchPage() {
  const searchParams = useSearchParams()
  const { checkPermission } = useAuth()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'relevance' | 'date' | 'title'>('relevance')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list')

  useEffect(() => {
    const searchQuery = searchParams.get('q')
    if (searchQuery) {
      performSearch(searchQuery)
    }
  }, [searchParams])

  const performSearch = async (searchQuery: string) => {
    setLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      // Filter mock results based on query
      const filteredResults = mockSearchResults.filter(result =>
        result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
      
      setResults(filteredResults)
      setLoading(false)
    }, 500)
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      performSearch(query.trim())
      // Update URL without navigation
      window.history.pushState({}, '', `/search?q=${encodeURIComponent(query.trim())}`)
    }
  }

  const filteredResults = results.filter(result => 
    selectedTypes.length === 0 || selectedTypes.includes(result.type)
  )

  const sortedResults = [...filteredResults].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return (b.lastModified?.getTime() || 0) - (a.lastModified?.getTime() || 0)
      case 'title':
        return a.title.localeCompare(b.title)
      default:
        return 0 // relevance - keep original order
    }
  })

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Most'
    if (diffInMinutes < 60) return `${diffInMinutes} perce`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} órája`
    return `${Math.floor(diffInMinutes / 1440)} napja`
  }

  const breadcrumbItems = createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Keresés' }
  ])

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Search className="h-6 w-6 mr-2" />
              Keresés
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Keresés a rendszer összes elemében
            </p>
          </div>
        </div>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Írja be a keresett kifejezést..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
          </div>
          
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="flex flex-wrap gap-2">
              {Object.entries(typeLabels).map(([type, label]) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => {
                    setSelectedTypes(prev => 
                      prev.includes(type) 
                        ? prev.filter(t => t !== type)
                        : [...prev, type]
                    )
                  }}
                  className={cn(
                    'px-3 py-1 text-sm rounded-full border transition-colors',
                    selectedTypes.includes(type)
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
            
            <button
              type="submit"
              disabled={!query.trim() || loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Keresés...' : 'Keresés'}
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {query && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {/* Results Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium text-gray-900">
                  Keresési eredmények
                </h2>
                <p className="text-sm text-gray-500">
                  {filteredResults.length} találat "{query}" kifejezésre
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                {/* Sort options */}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="relevance">Relevancia</option>
                  <option value="date">Dátum</option>
                  <option value="title">Név</option>
                </select>

                {/* View mode toggle */}
                <div className="flex rounded-md border border-gray-300">
                  <button
                    onClick={() => setViewMode('list')}
                    className={cn(
                      'p-2 text-sm',
                      viewMode === 'list'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-500 hover:text-gray-700'
                    )}
                  >
                    <List className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('grid')}
                    className={cn(
                      'p-2 text-sm',
                      viewMode === 'grid'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-500 hover:text-gray-700'
                    )}
                  >
                    <Grid className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Results List */}
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : sortedResults.length > 0 ? (
              <div className={cn(
                viewMode === 'grid' 
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
                  : 'space-y-4'
              )}>
                {sortedResults.map((result) => {
                  const Icon = typeIcons[result.type]
                  return (
                    <a
                      key={result.id}
                      href={result.url}
                      className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <Icon className="h-5 w-5 text-gray-400" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                              {typeLabels[result.type]}
                            </span>
                            {result.priority && (
                              <span className={cn(
                                'text-xs px-2 py-1 rounded border',
                                priorityColors[result.priority]
                              )}>
                                {result.priority === 'high' ? 'Magas' : 
                                 result.priority === 'medium' ? 'Közepes' : 'Alacsony'}
                              </span>
                            )}
                          </div>
                          
                          <h3 className="text-sm font-medium text-gray-900 truncate">
                            {result.title}
                          </h3>
                          
                          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                            {result.description}
                          </p>
                          
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-500">
                              {result.status}
                            </span>
                            {result.lastModified && (
                              <span className="text-xs text-gray-400 flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {formatTimeAgo(result.lastModified)}
                              </span>
                            )}
                          </div>
                          
                          {result.tags && result.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {result.tags.slice(0, 3).map((tag) => (
                                <span
                                  key={tag}
                                  className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      </div>
                    </a>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nincs találat
                </h3>
                <p className="text-gray-500">
                  Próbáljon más keresési kifejezést vagy módosítsa a szűrőket.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default withRequiredAuth(SearchPage)