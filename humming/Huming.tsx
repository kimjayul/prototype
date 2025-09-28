// src/pages/Huming/Huming.tsx

import React, { useState } from 'react';
import axios from 'axios';
import AudioUpload from './components/AudioUpload';
import DetailSelection from './components/DetailSelection';
import ProcessingPage from './components/ProcessingPage';
import CompletionPage from './components/CompletionPage';

// 백엔드 API로부터 받을 결과 데이터의 타입을 정의합니다.
interface ProcessingResult {
  musicUrl: string;
  title: string;
}

// 사용자가 선택할 음악 세부사항의 타입을 정의합니다.
interface MusicDetails {
  genre?: string;
  mood?: string;
  instrument?: string; // 단일 악기 선택으로 가정
  customPrompt?: string; // 사용자가 직접 입력하는 프롬프트
}

const Huming: React.FC = () => {
  // --- 1. 상태(State) 관리: 전체 프로세스의 데이터를 관리하는 변수들 ---
  
  // 현재 사용자가 어느 단계를 진행 중인지 기억합니다. (1:업로드, 2:세부선택, 3:처리중, 4:완료)
  const [currentStep, setCurrentStep] = useState(1);
  
  // 1단계(AudioUpload)에서 사용자가 업로드한 오디오 파일을 저장합니다.
  const [uploadedAudioFile, setUploadedAudioFile] = useState<File | null>(null);
  
  // 2단계(DetailSelection)에서 사용자가 선택한 음악 스타일을 저장합니다.
  const [selectedDetails, setSelectedDetails] = useState<MusicDetails>({});
  
  // 3단계(ProcessingPage)에서 백엔드 처리 중 발생한 오류 메시지를 저장합니다.
  const [processingError, setProcessingError] = useState('');
  
  // 4단계(CompletionPage)에서 최종적으로 생성된 음악 정보를 저장합니다.
  const [completionResult, setCompletionResult] = useState<ProcessingResult | null>(null);

  // --- 2. 이벤트 핸들러: 각 단계의 컴포넌트와 상호작용하는 함수들 ---

  /**
   * 1단계(AudioUpload)가 완료되면 실행되는 함수.
   * 업로드된 파일을 상태에 저장하고, 2단계로 넘어갑니다.
   */
  const handleAudioUpload = (file: File) => {
    console.log("1단계 완료: 오디오 파일 수신", file.name);
    setUploadedAudioFile(file);
    setCurrentStep(2); // 다음 단계(세부사항 선택)로 이동
  };

  /**
   * 2단계(DetailSelection)가 완료되면 실행되는 함수.
   * 이것이 백엔드 API 호출의 "방아쇠" 역할을 합니다.
   */
  const handleDetailsSubmit = async (details: MusicDetails) => {
    console.log("2단계 완료: 세부사항 수신", details);
    setSelectedDetails(details);
    setCurrentStep(3); // 다음 단계(처리 중 화면)로 즉시 이동

    if (!uploadedAudioFile) {
      setProcessingError("오류: 오디오 파일이 없습니다. 이전 단계로 돌아가세요.");
      return;
    }

    // FormData에 모든 데이터를 담아 백엔드로 전송 준비
    const formData = new FormData();
    formData.append('audio', uploadedAudioFile);
    formData.append('genre', details.genre || 'Pop Ballad'); // 기본값 설정
    formData.append('mood', details.mood || 'Happy'); // 기본값 설정
    // DetailSelection 컴포넌트는 단일 악기 선택이므로, 배열 대신 단일 값으로 보냅니다.
    // 만약 다중 선택으로 변경 시, 이전처럼 instruments[]로 보내야 합니다.
    formData.append('instruments[]', details.instrument || 'Piano');
    formData.append('custom_prompt', details.customPrompt || '');

    try {
      // 백엔드 API 호출
      console.log("3단계 시작: 백엔드에 음악 생성 요청...");
      const response = await axios.post('http://localhost:5000/generate-music', formData);
      
      const backendUrl = 'http://localhost:5000';
      
      // API 호출 성공 시, 결과 정보를 상태에 저장하고 4단계로 이동
      const result: ProcessingResult = {
        musicUrl: backendUrl + response.data.audio_url,
        title: response.data.title || "새로운 음악",
      };
      console.log("3단계 완료: 음악 생성 성공!", result.musicUrl);
      setCompletionResult(result);
      setCurrentStep(4);

    } catch (err: any) {
      console.error("3단계 오류: API 호출 실패", err);
      // API 호출 실패 시, 에러 메시지를 상태에 저장하고 4단계로 이동 (에러 표시를 위해)
      const errorMessage = err.response?.data?.error || '알 수 없는 서버 오류가 발생했습니다.';
      setProcessingError(errorMessage);
      setCurrentStep(4); // 오류가 발생해도 완료 페이지로 넘어가서 메시지를 보여줌
    }
  };

  /**
   * 4단계(CompletionPage)에서 '다시 만들기'를 누르면 실행되는 함수.
   * 모든 상태를 초기화하고 1단계로 돌아갑니다.
   */
  const handleRegenerate = () => {
    console.log("4단계: 다시 만들기 요청. 모든 과정을 초기화합니다.");
    setCurrentStep(1);
    setUploadedAudioFile(null);
    setSelectedDetails({});
    setProcessingError('');
    setCompletionResult(null);
  };

  // --- 3. UI 렌더링: 현재 단계에 맞는 컴포넌트를 화면에 표시 ---

  // 현재 단계(currentStep)에 따라 다른 컴포넌트를 보여줍니다.
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <AudioUpload onAudioUpload={handleAudioUpload} />;
      case 2:
        return <DetailSelection onDetailsSubmit={handleDetailsSubmit} />;
      case 3:
        // ProcessingPage는 자체적으로 로딩 애니메이션을 보여주고,
        // 실제 처리는 handleDetailsSubmit 함수가 백그라운드에서 수행합니다.
        return <ProcessingPage onProcessingComplete={() => {}} />; // 이 페이지는 이제 시각적 효과만 담당
      case 4:
        if (processingError) {
          // 오류가 발생했다면, 완료 페이지에서 오류 메시지를 보여줄 수 있습니다.
          // (CompletionPage가 오류를 표시하는 기능을 지원한다고 가정)
          return <CompletionPage onRegenerate={handleRegenerate} result={{musicUrl: '', title: `오류: ${processingError}`}} details={selectedDetails} />;
        }
        return <CompletionPage onRegenerate={handleRegenerate} result={completionResult!} details={selectedDetails} />;
      default:
        return <AudioUpload onAudioUpload={handleAudioUpload} />;
    }
  };

  return (
    <div>
      {/* ProcessFlow 컴포넌트는 이제 사용하지 않고, 
        Huming.tsx가 직접 현재 단계에 맞는 화면을 렌더링하도록 변경합니다.
      */}
      {renderCurrentStep()}
    </div>
  );
};

export default Huming;