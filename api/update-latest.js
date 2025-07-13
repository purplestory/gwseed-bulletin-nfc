import { writeFile, readFile } from 'fs/promises';
import { join } from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // 교회 웹사이트에서 최신 주보 정보 가져오기
    const response = await fetch('https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();
    
    // wr_id 패턴으로 최신 주보 찾기
    const wrIdMatch = html.match(/wr_id=(\d+)/);
    if (!wrIdMatch) {
      throw new Error('No wr_id found in HTML');
    }

    const wrId = wrIdMatch[1];
    const latestUrl = `https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id=${wrId}`;
    
    // 최신 주보 정보 저장
    const bulletinInfo = {
      url: latestUrl,
      wr_id: wrId,
      timestamp: new Date().toISOString()
    };

    // 파일에 저장 (Vercel에서는 임시 파일 시스템 사용)
    const filePath = join(process.cwd(), 'latest_bulletin.json');
    await writeFile(filePath, JSON.stringify(bulletinInfo, null, 2));

    // index.html 업데이트
    try {
      const indexPath = join(process.cwd(), 'index.html');
      let indexContent = await readFile(indexPath, 'utf8');
      
      // wr_id 패턴 찾기 및 교체
      const updatedContent = indexContent.replace(/wr_id=\d+/g, `wr_id=${wrId}`);
      
      await writeFile(indexPath, updatedContent);
      console.log(`✅ index.html 업데이트 완료: wr_id=${wrId}`);
    } catch (indexError) {
      console.error('❌ index.html 업데이트 실패:', indexError);
    }

    console.log(`✅ 최신 주보 업데이트: ${latestUrl}`);
    
    return res.status(200).json({
      success: true,
      bulletin: bulletinInfo
    });

  } catch (error) {
    console.error('❌ 업데이트 실패:', error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
} 