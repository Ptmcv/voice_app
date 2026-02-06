# utils/audio_processor.py
"""Обработка аудио файлов"""

import os

class AudioProcessor:
    """Инструменты для обработки аудио"""
    
    @staticmethod
    def add_end_pause(audio_file, pause_seconds):
        """Добавить паузу в конец аудио"""
        try:
            # Используем moviepy вместо pydub
            from moviepy.editor import AudioFileClip, concatenate_audioclips
            
            audio = AudioFileClip(audio_file)
            
            # Создаем тишину
            from moviepy.editor import AudioClip
            silence = AudioClip(lambda t: 0, duration=pause_seconds)
            silence = silence.set_fps(audio.fps)
            
            # Соединяем
            final_audio = concatenate_audioclips([audio, silence])
            final_audio.write_audiofile(audio_file, codec='mp3')
            
            audio.close()
            final_audio.close()
            
            return True, "Пауза добавлена"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def adjust_duration(audio_file, target_duration):
        """Изменить длительность аудио"""
        try:
            from moviepy.editor import AudioFileClip
            
            audio = AudioFileClip(audio_file)
            current_duration = audio.duration
            
            if current_duration == 0:
                return False, "Аудио пустое"
            
            speed_ratio = current_duration / target_duration
            
            # Изменяем скорость
            new_audio = audio.fx(lambda clip: clip.speedx(speed_ratio))
            new_audio.write_audiofile(audio_file, codec='mp3')
            
            audio.close()
            new_audio.close()
            
            return True, f"Длительность изменена: {current_duration:.2f}s → {target_duration:.2f}s"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_duration(audio_file):
        """Получить длительность аудио"""
        try:
            from moviepy.editor import AudioFileClip
            audio = AudioFileClip(audio_file)
            duration = audio.duration
            audio.close()
            return duration
        except:
            return 0
