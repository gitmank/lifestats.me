import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ username: string; keyId: string }> }
) {
  try {
    const { username, keyId } = await params;
    const authHeader = request.headers.get('authorization');
    
    const response = await fetch(`${API_BASE_URL}/api/keys/${username}/${keyId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
    });

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json();
    
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Delete API key by ID proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
} 