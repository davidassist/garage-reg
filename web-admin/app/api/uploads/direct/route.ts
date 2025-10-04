import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

// Direct upload endpoint (mock S3)
export async function PUT(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const key = searchParams.get('key')
    const contentType = searchParams.get('contentType')
    const expires = searchParams.get('expires')
    
    if (!key) {
      return NextResponse.json(
        { error: 'Missing key parameter' },
        { status: 400 }
      )
    }
    
    // Check if URL has expired
    if (expires && parseInt(expires) < Date.now()) {
      return NextResponse.json(
        { error: 'Upload URL has expired' },
        { status: 410 }
      )
    }
    
    // Get file data
    const buffer = Buffer.from(await request.arrayBuffer())
    
    // Save to local storage (in production this would be S3)
    const uploadDir = join(process.cwd(), 'uploads')
    if (!existsSync(uploadDir)) {
      await mkdir(uploadDir, { recursive: true })
    }
    
    const fileName = key.split('/').pop() || 'unknown'
    const filePath = join(uploadDir, fileName)
    
    await writeFile(filePath, buffer)
    
    // Return success with URL
    const fileUrl = `/uploads/${fileName}`
    
    return new NextResponse(null, { 
      status: 200,
      headers: {
        'ETag': `"${Date.now()}"`, // Mock ETag
        'Location': fileUrl
      }
    })
    
  } catch (error) {
    console.error('Direct upload error:', error)
    return NextResponse.json(
      { error: 'Upload failed' },
      { status: 500 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'PUT, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}