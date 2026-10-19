with open('templates/tutorial.html', 'r', encoding='utf-8') as f:
    t = f.read()

# Replace the video tag with direct src and fallback
start_mark = '<!-- HTML5 Video Player -->'
end_mark = '</video>'

start_idx = t.find(start_mark)
end_idx = t.find(end_mark)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_mark)
    new_video_tag = '''<!-- HTML5 Video Player -->
          <video id="tutorial-player" class="tutorial-video-element" controls playsinline preload="auto" src="/static/videos/how-to-buy.mp4">
            <source src="/static/videos/how-to-buy.mp4" type="video/mp4">
            <source src="/static/videos/how-to-buy.MOV" type="video/quicktime">
            Your browser does not support HTML5 video playback.
          </video>'''
    t = t[:start_idx] + new_video_tag + t[end_idx:]
    with open('templates/tutorial.html', 'w', encoding='utf-8') as f:
        f.write(t)
    print('tutorial.html video tag updated successfully')
else:
    print('Marks not found:', start_idx, end_idx)
