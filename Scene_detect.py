#Nessecary Imports 
from scenedetect import SceneManager, ContentDetector, open_video
import cv2
#scene detection function
def get_scene_boundaries_from_video(video_path) -> list:
    """
    Analyzes the video at the given path and returns a list of scene boundaries.
    
    Args:
        video_path (str): The path to the video file.
    Output:
        List of scenes,  each containing the start and end time (in seconds) of a scene.
    """
    video_path = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    scene_manager.detect_scenes(video_path,show_progress=True)
    scene_list = scene_manager.get_scene_list()
    print (scene_list)
    return [f'scene - {scene+1} {start.get_seconds()}, {end.get_seconds()}' for scene,(start, end) in enumerate(scene_list)]

if __name__ == "__main__":
    video_path = r"sample_tests\Video-855.mp4"  # Replace with your video path
    scenes = get_scene_boundaries_from_video(video_path)
    print (scenes)