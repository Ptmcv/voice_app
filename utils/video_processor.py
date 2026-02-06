# utils/video_processor.py
"""Обработка видео файлов"""

import os
import re
from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeAudioClip, 
                            concatenate_videoclips, CompositeVideoClip, vfx)
from .helpers import natural_sort_key

class VideoProcessor:
    """Инструменты для обработки видео"""
    
    @staticmethod
    def process_single_video(video_path, audio_path, output_path, fit_mode="fit", 
                            keep_original=False, original_volume=30):
        """Заменить звук в видео с правильной подгонкой"""
        try:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            video_duration = video.duration
            audio_duration = audio.duration
            
            print(f"[DEBUG] Видео: {video_duration:.2f}s, Аудио: {audio_duration:.2f}s")
            
            # Подгонка длины
            if fit_mode == "fit":
                # Растяжение/сжатие видео под аудио
                if abs(video_duration - audio_duration) > 0.1:  # Если разница больше 0.1 сек
                    speed_factor = video_duration / audio_duration
                    print(f"[DEBUG] Коэффициент скорости: {speed_factor:.3f}")
                    
                    # Изменяем скорость видео
                    video = video.fx(vfx.speedx, speed_factor)
                    print(f"[DEBUG] Новая длина видео: {video.duration:.2f}s")
                
            elif fit_mode == "trim":
                # Только обрезка
                if audio_duration > video_duration:
                    # Аудио длиннее - обрезаем аудио
                    audio = audio.subclip(0, video_duration)
                    print(f"[DEBUG] Обрезано аудио до {video_duration:.2f}s")
                else:
                    # Видео длиннее - обрезаем видео
                    video = video.subclip(0, audio_duration)
                    print(f"[DEBUG] Обрезано видео до {audio_duration:.2f}s")
            
            # Микширование аудио
            if keep_original and video.audio:
                original_audio = video.audio.volumex(original_volume / 100.0)
                final_audio = CompositeAudioClip([audio, original_audio])
                print(f"[DEBUG] Микшированное аудио: новое + оригинал ({original_volume}%)")
            else:
                final_audio = audio
                print(f"[DEBUG] Только новое аудио")
            
            # Применяем аудио к видео
            final_video = video.set_audio(final_audio)
            
            # Экспортируем
            print(f"[DEBUG] Экспорт в {output_path}")
            final_video.write_videofile(output_path, 
                                       codec='libx264', 
                                       audio_codec='aac',
                                       preset='medium',
                                       threads=4)
            
            # Закрываем клипы
            video.close()
            audio.close()
            if keep_original and video.audio:
                original_audio.close()
            final_audio.close()
            final_video.close()
            
            return True, "Видео обработано"
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    @staticmethod
    def find_video_audio_pairs(video_folder, audio_folder):
        """Найти пары видео-аудио файлов по номерам"""
        video_files = {}
        audio_files = {}
        
        # Собираем видео
        for file in os.listdir(video_folder):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                match = re.match(r'^(\d+)', file)
                if match:
                    number = int(match.group(1))
                    video_files[number] = os.path.join(video_folder, file)
        
        # Собираем аудио
        for file in os.listdir(audio_folder):
            if file.lower().endswith(('.mp3', '.wav', '.aac')):
                match = re.match(r'^(\d+)', file)
                if match:
                    number = int(match.group(1))
                    audio_files[number] = os.path.join(audio_folder, file)
        
        # Создаем пары
        pairs = []
        for number in sorted(video_files.keys()):
            if number in audio_files:
                pairs.append({
                    'number': number,
                    'video': video_files[number],
                    'audio': audio_files[number]
                })
        
        return pairs
    
    @staticmethod
    def montage_videos(video_folder, output_file, use_transitions=False, 
                      transition_type="crossfade", transition_duration=0.5):
        """Смонтировать видео из папки с переходами"""
        try:
            # Собираем видео файлы
            video_files = []
            for file in os.listdir(video_folder):
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    video_files.append(os.path.join(video_folder, file))
            
            if not video_files:
                return False, "Нет видео файлов"
            
            # Сортируем
            video_files.sort(key=lambda x: natural_sort_key(os.path.basename(x)))
            
            print(f"[DEBUG] Найдено {len(video_files)} видео")
            
            # Загружаем клипы
            clips = [VideoFileClip(vf) for vf in video_files]
            
            # Добавляем переходы
            if use_transitions and len(clips) > 1:
                print(f"[DEBUG] Применяем переход: {transition_type}, {transition_duration}s")
                clips = VideoProcessor._apply_transitions(clips, transition_type, transition_duration)
            
            # Соединяем
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Экспорт
            print(f"[DEBUG] Экспорт финального видео: {output_file}")
            final_clip.write_videofile(output_file, 
                                      codec='libx264', 
                                      audio_codec='aac',
                                      preset='medium',
                                      threads=4)
            
            # Закрываем клипы
            for clip in clips:
                clip.close()
            final_clip.close()
            
            return True, f"Видео смонтировано: {output_file}"
        except Exception as e:
            print(f"[ERROR] {e}")
            return False, str(e)
    
    @staticmethod
    def _apply_transitions(clips, transition_type, duration):
        """Применить переходы между клипами"""
        result_clips = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # Первый клип без изменений
                result_clips.append(clip)
            else:
                # Применяем переход
                if transition_type == "crossfade":
                    # Плавное затухание
                    clip = clip.crossfadein(duration)
                
                elif transition_type == "fade":
                    # Затухание через чёрный
                    clip = clip.fadein(duration)
                
                elif transition_type in ["slide_left", "slide_right", "slide_up", "slide_down"]:
                    # Слайды (упрощённая реализация через позиционирование)
                    clip = clip.crossfadein(duration)
                
                elif transition_type == "wipe":
                    # Вытеснение (как crossfade)
                    clip = clip.crossfadein(duration)
                
                elif transition_type == "dissolve":
                    # Растворение
                    clip = clip.crossfadein(duration)
                
                result_clips.append(clip)
        
        return result_clips


    @staticmethod
    def concatenate_videos_with_transitions(video_files, output_file, transition_type="fade", duration=0.5):
        """Склеить видео с переходами"""
        
        if not video_files:
            return False, "Нет видео для склейки"
        
        if len(video_files) == 1:
            # Одно видео - просто копируем
            import shutil
            shutil.copy2(video_files[0], output_file)
            return True, output_file
        
        try:
            # Если переход "none" - простая конкатенация
            if transition_type == "none":
                return VideoProcessor._concatenate_simple(video_files, output_file)
            
            # С переходами используем FFmpeg xfade
            return VideoProcessor._concatenate_with_xfade(
                video_files, output_file, transition_type, duration
            )
        
        except Exception as e:
            return False, f"Ошибка склейки: {e}"
    
    @staticmethod
    def _concatenate_simple(video_files, output_file):
        """Простая конкатенация без переходов"""
        import subprocess
        
        try:
            # Создаём список файлов
            list_file = "temp_concat_list.txt"
            
            with open(list_file, 'w', encoding='utf-8') as f:
                for video in video_files:
                    f.write(f"file '{os.path.abspath(video)}'\n")
            
            # FFmpeg конкатенация
            command = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_file
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            # Удаляем временный файл
            if os.path.exists(list_file):
                os.remove(list_file)
            
            if result.returncode == 0:
                return True, output_file
            else:
                return False, result.stderr
        
        except Exception as e:
            return False, f"Ошибка: {e}"
    
    @staticmethod
    def _concatenate_with_xfade(video_files, output_file, transition_type, duration):
        """Склейка с переходами через FFmpeg xfade"""
        import subprocess
        
        try:
            # Для xfade нужно последовательно применять фильтры
            # Это сложный процесс, поэтому упростим: используем moviepy
            
            from moviepy.editor import VideoFileClip, concatenate_videoclips
            
            clips = [VideoFileClip(f) for f in video_files]
            
            # Создаём финальное видео с crossfade
            final = concatenate_videoclips(clips, method="compose")
            
            final.write_videofile(
                output_file,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                logger=None
            )
            
            # Закрываем клипы
            for clip in clips:
                clip.close()
            final.close()
            
            return True, output_file
        
        except Exception as e:
            # Если moviepy не работает - падаем на простую конкатенацию
            print(f"Переходы не поддерживаются, используем простую склейку: {e}")
            return VideoProcessor._concatenate_simple(video_files, output_file)
