import { readFile } from 'fs/promises';
import { join } from 'path';

export default async function handler(req, res) {
  try {
    // 저장된 최신 주보 정보 읽기
    const filePath = join(process.cwd(), 'latest_bulletin.json');
    const fileContent = await readFile(filePath, 'utf-8');
    const bulletinInfo = JSON.parse(fileContent);

    return res.status(200).json(bulletinInfo);

  } catch (error) {
    console.error('❌ 최신 주보 정보 읽기 실패:', error);
    
    // 파일이 없거나 읽기 실패 시 기본값 반환
    return res.status(200).json({
      url: "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly",
      wr_id: null,
      timestamp: new Date().toISOString()
    });
  }
} 