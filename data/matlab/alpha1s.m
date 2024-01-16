
function a=alpha()
Fs = 8000;
Mic = audioDeviceReader(Fs);
record = zeros(1);
while(true)
    audio = step(Mic);  % Micから入力読み込み
    record = vertcat(record, audio); 
    myRecording = partvec(record,1*Fs);
    xlabel('時間[s]');
    
    if length(myRecording) < Fs*1  % 計測時間が2s以下なら残りの解析をしない
       continue 
    end
    [A,B,C,D] = butter(2,[5 15]/(Fs/2));  % フィルターの係数？
    sos = ss2sos(A,B,C,D);                % 係数からフィルターへ
    
    signal_in = myRecording;
    signal_out = sosfilt(sos,signal_in);  % 信号に作ったフィルターを掛ける
    eeg = signal_out;

    a=rms(eeg);
    break

end

   



