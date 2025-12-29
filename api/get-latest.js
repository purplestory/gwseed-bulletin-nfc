export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // GitHub에서 최신 주보 정보 읽기 (항상 최신 버전)
    const githubRawUrl = 'https://raw.githubusercontent.com/purplestory/gwseed-bulletin-nfc/main/latest_bulletin.json';
    const response = await fetch(githubRawUrl, {
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      }
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }

    const bulletinInfo = await response.json();
    return res.status(200).json(bulletinInfo);

  } catch (error) {
    console.error('❌ 최신 주보 정보 읽기 실패:', error);
    
    // 파일이 없거나 읽기 실패 시 주보 리스트 페이지 URL만 반환
    return res.status(200).json({
      url: "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly",
      wr_id: null,
      timestamp: new Date().toISOString()
    });
  }
} 