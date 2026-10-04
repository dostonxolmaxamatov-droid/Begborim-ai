import json, math, struct, subprocess, tempfile, unittest, wave
from pathlib import Path
import storyboard

class StoryboardTests(unittest.TestCase):
    def test_unreadable_caption_cannot_be_silently_invented(self):
        scene={'readable':False,'visible_text':'','action_prompt':'Invented motion','narration':'Look here'}
        with self.assertRaises(ValueError):storyboard.validate_scene(scene,True,'en',5)
        scene.update(readable=True,visible_text='The tiny door appears.',action_prompt='A tiny door appears.',narration='Eshik paydo bo‘ldi.')
        self.assertEqual(storyboard.validate_scene(scene,True,'uz',4)['narration'],'Eshik paydo bo‘ldi.')
        with self.assertRaises(ValueError):storyboard.validate_scene(scene,True,'uz',1)

    def test_actual_audio_fit_mux_and_language_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);source=folder/'source.wav';audio=folder/'audio.wav';video=folder/'video.mp4'
            with wave.open(str(source),'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000)
                w.writeframes(b''.join(struct.pack('<h',int(8000*math.sin(i*2*math.pi*440/24000))) for i in range(36000)))
            storyboard.fit_voice(source,30,audio)
            with wave.open(str(audio)) as w:self.assertEqual(w.getnframes(),24000)
            subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=blue:s=64x64:r=30','-t','1','-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(video)],check=True)
            storyboard.mux_voice(video,audio,1,'uz')
            streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))['streams']
            self.assertEqual(next(s for s in streams if s['codec_type']=='video')['nb_frames'],'30')
            self.assertEqual(next(s for s in streams if s['codec_type']=='audio')['tags']['language'],'uzb')


if __name__=="__main__":unittest.main()
