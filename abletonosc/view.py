from functools import partial
from typing import Optional, Tuple, Any
from .handler import AbletonOSCHandler

import Live

class ViewHandler(AbletonOSCHandler):
    def __init__(self, manager):
        super().__init__(manager)
        self.class_identifier = "view"

    def init_api(self):
        def get_selected_scene(params: Optional[Tuple] = ()):
            return (list(self.song.scenes).index(self.song.view.selected_scene),)

        def get_selected_track(params: Optional[Tuple] = ()):
            return (list(self.song.tracks).index(self.song.view.selected_track),)

        def get_detail_clip(params: Optional[Tuple] = ()):
            self.logger.info("get_detail_clip")
            # for attr in dir(self.song.view):
            #     self.logger.info("attribute:", attr)
            #     self.logger.info("obj.%s = %r" % (attr, getattr(self.song.view, attr)))

            for attr in dir(self.song.view.detail_clip):
                try:
                    self.logger.info("attribute:", attr)
                    self.logger.info("obj.%s = %r" % (attr, getattr(self.song.view.detail_clip, attr)))
                except:
                    pass

        def get_detail_clip_full(params: Optional[Tuple] = ()):
            """
            Get details and notes of a clip given the track and clip index.
            """
            clip = self.song.view.detail_clip
            self.logger.info("get_detail_clip_full", clip)
            
            details = [
                clip.name,
                clip.length,
                clip.signature_numerator,
                clip.signature_denominator,
                clip.start_marker,
                clip.end_marker,
                clip.loop_start,
                clip.loop_end
            ]
            notes = clip.get_notes_extended(0, 127, -8192, 16384)
            all_note_attributes = []
            for note in notes:
                all_note_attributes += [note.pitch, note.start_time, note.duration, note.velocity, note.mute]
            return tuple(details + all_note_attributes)

        def get_full_selected_clip(params):
            """
            Get track index, clip index, details and notes of the selected clip.
            """
            track_index = get_selected_track()[0]
            clip_index = get_selected_scene()[0]
            clip = self.song.tracks[track_index].clip_slots[clip_index].clip
            self.logger.info("get_selected_clip_full", track_index, clip_index, clip)
            if clip is None:
                return tuple([track_index])
            details = [
                clip.name,
                clip.length,
                clip.signature_numerator,
                clip.signature_denominator,
                clip.start_marker,
                clip.end_marker,
                clip.loop_start,
                clip.loop_end
            ]
            notes = clip.get_notes_extended(0, 127, -8192, 16384)
            all_note_attributes = []
            for note in notes:
                all_note_attributes += [note.pitch, note.start_time, note.duration, note.velocity, note.mute]
            return tuple([track_index, clip_index] + details + all_note_attributes)

        def detail_clip_get_details(params: Optional[Tuple] = ()):

            return tuple([
                self.song.view.detail_clip.name,
                self.song.view.detail_clip.length,
                self.song.view.detail_clip.signature_numerator,
                self.song.view.detail_clip.signature_denominator,
                self.song.view.detail_clip.start_time,
                self.song.view.detail_clip.end_time,
                self.song.view.detail_clip.loop_start,
                self.song.view.detail_clip.loop_end
            ])

        def detail_clip_get_notes(params: Optional[Tuple] = ()):
            self.logger.info("detail_clip_get_notes")
            if len(params) == 4:
                pitch_start, pitch_span, time_start, time_span = params
            elif len(params) == 0:
                pitch_start, pitch_span, time_start, time_span = 0, 127, -8192, 16384
            else:
                raise ValueError("Invalid number of arguments for /clip/get/notes. Either 0 or 4 arguments must be passed.")
            notes = self.song.view.detail_clip.get_notes_extended(pitch_start, pitch_span, time_start, time_span)
            all_note_attributes = []
            for note in notes:
                all_note_attributes += [note.pitch, note.start_time, note.duration, note.velocity, note.mute]
            return tuple(all_note_attributes)

        def detail_clip_add_notes(params: Optional[Tuple] = ()):
            notes = []
            for offset in range(0, len(params), 5):
                pitch, start_time, duration, velocity, mute = params[offset:offset + 5]
                note = Live.Clip.MidiNoteSpecification(start_time=start_time,
                                                       duration=duration,
                                                       pitch=pitch,
                                                       velocity=velocity,
                                                       mute=mute)
                notes.append(note)
            self.song.view.detail_clip.add_new_notes(tuple(notes))

        def detail_clip_remove_notes(params: Optional[Tuple] = ()):
            if len(params) == 4:
                pitch_start, pitch_span, time_start, time_span = params
            elif len(params) == 0:
                pitch_start, pitch_span, time_start, time_span = 0, 127, -8192, 16384
            else:
                raise ValueError("Invalid number of arguments for /clip/remove/notes. Either 0 or 4 arguments must be passed.")
            self.song.view.detail_clip.remove_notes_extended(pitch_start, pitch_span, time_start, time_span)

        def get_selected_clip(params: Optional[Tuple] = ()):
            return (get_selected_track()[0], get_selected_scene()[0])
        
        def get_selected_device(params: Optional[Tuple] = ()):
            return (get_selected_track()[0], list(self.song.view.selected_track.devices).index(self.song.view.selected_track.view.selected_device))

        def set_selected_scene(params: Optional[Tuple] = ()):
            self.song.view.selected_scene = self.song.scenes[params[0]]

        def set_selected_track(params: Optional[Tuple] = ()):
            self.song.view.selected_track = self.song.tracks[params[0]]

        def set_selected_clip(params: Optional[Tuple] = ()):
            set_selected_track((params[0],))
            set_selected_scene((params[1],))

        def set_selected_device(params: Optional[Tuple] = ()):
            device = self.song.tracks[params[0]].devices[params[1]]
            self.song.view.select_device(device)
            return params[0], params[1]

        self.osc_server.add_handler("/live/view/get/detail_clip", get_detail_clip)
        self.osc_server.add_handler("/live/view/detail_clip/get/details", detail_clip_get_details)
        self.osc_server.add_handler("/live/view/detail_clip/get/notes", detail_clip_get_notes)
        self.osc_server.add_handler("/live/view/detail_clip/add/notes", detail_clip_add_notes)
        self.osc_server.add_handler("/live/view/detail_clip/remove/notes", detail_clip_remove_notes)
        self.osc_server.add_handler("/live/view/get/selected_scene", get_selected_scene)
        self.osc_server.add_handler("/live/view/get/selected_track", get_selected_track)
        self.osc_server.add_handler("/live/view/get/selected_clip", get_selected_clip)
        self.osc_server.add_handler("/live/view/get/full/selected_clip", get_full_selected_clip)
        self.osc_server.add_handler("/live/view/get/selected_device", get_selected_device)
        self.osc_server.add_handler("/live/view/set/selected_scene", set_selected_scene)
        self.osc_server.add_handler("/live/view/set/selected_track", set_selected_track)
        self.osc_server.add_handler("/live/view/set/selected_clip", set_selected_clip)
        self.osc_server.add_handler("/live/view/set/selected_device", set_selected_device)
        
        self.osc_server.add_handler('/live/view/start_listen/selected_scene', partial(self._start_listen, self.song.view, "selected_scene", getter=get_selected_scene))
        self.osc_server.add_handler('/live/view/start_listen/selected_track', partial(self._start_listen, self.song.view, "selected_track", getter=get_selected_track))
        self.osc_server.add_handler('/live/view/stop_listen/selected_scene', partial(self._stop_listen, self.song.view, "selected_scene"))
        self.osc_server.add_handler('/live/view/stop_listen/selected_track', partial(self._stop_listen, self.song.view, "selected_track"))
