# FFmpeg based PyTool for easy Video transcoding and processing
###############################################################


# Module Imports
import os
import sys
import json
from subprocess import call, check_output

# Global Initianlistions
global standard_resolutions
global default_compression_opts
global default_bitrate_opts
global default_audio_bitrates

standard_resolutions     = ["2160","1080","720","480","360"]
default_compression_opts = {"crf":"18","preset":"slow","keyint":"-g 48 -sc_threshold 0 -keyint_min 48"}
default_bitrate_opts   = {"2160":{"vrate":"5M","min":"5M","max":"5M","buf":"10M","video_opts":"","arate":"","audio_opts":""},
                              "1080":{"vrate":"5M","min":"5M","max":"5M","buf":"10M","video_opts":"","arate":"","audio_opts":""},
                              "720" :{"vrate":"3M","min":"3M","max":"3M","buf":"3M" ,"video_opts":"","arate":"","audio_opts":""},
                              "480" :{"vrate":"1M","min":"1M","max":"1M","buf":"1M" ,"video_opts":"","arate":"","audio_opts":""},
                              "360" :{"vrate":"1M","min":"1M","max":"1M","buf":"1M" ,"video_opts":"","arate":"","audio_opts":""}}
default_audio_bitrates = {"aac":{"2160":"128k","1080":"96k","720":"96k","480":"48k","360":"48k"},
                                 "ac3" :{"2160":"640k","1080":"640k","720":"640k","480":"640k","360":"640k"},
                                 "ec3" :{"2160":"640k","1080":"640k","720":"640k","480":"640k","360":"640k"},
                                 "eac3":{"2160":"640k","1080":"640k","720":"640k","480":"640k","360":"640k"}}

def get_default_opts(video_codec,audio_codec):
    if video_codec.upper() in ["H.265","H265"]:
        video_opts = "profile=main"
    elif video_codec.upper() in ["H.264","H264"]:
        video_opts = "nal-hrd=cbr:force-cfr=1"

    if audio_codec.upper() == "AAC":
        audio_opts = "-ac 2"
    elif audio_codec.upper() in  ["AC3","EC3","EAC3"]:
        audio_opts = "-ac 6"
    global default_bitrate_opts
    for res in standard_resolutions:
        default_bitrate_opts[res]["video_opts"] = video_opts
        default_bitrate_opts[res]["audio_opts"] = audio_opts
        default_bitrate_opts[res]["arate"] = default_audio_bitrates.get(audio_codec.lower()).get(res)



def get_codec_info(input_file,channel):
    output = check_output(['ffprobe', '-v', 'error', '-select_streams', channel,
                            '-show_entries', 'stream=codec_name', '-of', 
                            'default=nokey=1:noprint_wrappers=1', input_file])
    #ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1

    return output.decode('utf-8').split()    

def start_play_back(src_file):
    play_command = "ffplay " + src_file
    os.system(play_command)

def demuxer(input_file,output_format):
    basefilepath, extension = os.path.splitext(input_file)
    if output_format == "Audio":
        output_file = basefilepath + '_Audio_Only' + extension
        dem_command = "ffmpeg -i " + input_file + " -vn -acodec copy " + output_file
        print (dem_command)
        os.system(dem_command)

    if output_format == "Video":
        output_file = basefilepath + '_Video_Only' + extension
        dem_command = "ffmpeg -i " + input_file + " -an -vcodec copy " + output_file
        print (dem_command)
        os.system(dem_command)
    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back(output_file)

def muxer(input_video,input_audio):
    basefilepath, extension = os.path.splitext(input_video)
    output_file = basefilepath + "_Audio_New" + extension
    mux_command = "ffmpeg -i " + input_video + " -i " + input_audio + " -c:v copy -c:a copy -map 0:v:0 -map 1:a:0 " + output_file
    print (mux_command)
    os.system(mux_command)
    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back(output_file)

def stream_cutter(input_file,duration):
    basefilepath, extension = os.path.splitext(input_file)
    output_file = basefilepath + "_" + str(duration) + extension    
    cut_command = "ffmpeg -i " + input_file + " -ss 00:00:00 -t 00:00:"+str(duration) + " -async 1 " + output_file
    print (cut_command)
    os.system(cut_command)
    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back(output_file)

def subtitle_adder(input_file,srt_file):
    basefilepath, extension = os.path.splitext(input_file)
    output_file = basefilepath + "_Subtitled" + extension
    sub_command  = "ffmpeg -i " + input_file + " -i "  + srt_file +" -c:s mov_text -vf subtitles="+srt_file + " " + output_file
    print (sub_command)
    os.system(sub_command)
    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back(output_file)



def subtitle_extractor(input_file):
    basefilepath, extension = os.path.splitext(input_file)
    output_file = basefilepath + "_Subtitle.srt"
    sub_command = "ffmpeg -i " + input_file + " -vn -an -codec:s srt " + output_file
    print (sub_command)
    os.system(sub_command)
    display_command = "cat " + output_file
    os.system(display_command)


def stream_analyser(input_file):
    analyse_command = "ffprobe -v error -show_format -show_streams " + input_file
    print (analyse_command)
    os.system(analyse_command)


def transcoder(input_file,av_codec,av_info,comp_info,encoding_type="CRF"):
    print "yes"

    basefilepath, extension = os.path.splitext(input_file)


    actual_video_codec = get_codec_info(input_file, 'v:0')
    if actual_video_codec == []:
        print "\n[ERROR]: No Video Codec identified in the provided stream. Exiting..."
        return
    actual_audio_codec = get_codec_info(input_file, 'a:0')

    video_codec = av_codec["vcodec_name"]
    audio_codec = av_codec["acodec_name"]
    print video_codec,audio_codec

    ###########################################################
    # Transcoding to H265/HEVC video codec
    ###########################################################
    if video_codec in ["H.265","HEVC"]:
        output_file = basefilepath + '_H265_' +audio_codec.upper()+ extension

        if encoding_type == "CRF":
            if 'hevc' in actual_video_codec or 'hvc1' in actual_video_codec:
                default_video_opts = "-c:v copy"
                print "[INFO]: Input Video is already in H265/HEVC format.Copying Video"
            else:
                default_video_opts = "-c:v "+av_codec["vcodec"]

            compression_opts = '-tag:v hvc1 -crf '+comp_info["crf"]+' -preset '+comp_info["preset"]

            if actual_audio_codec != []:
                if audio_codec.lower() in actual_audio_codec:
                    default_audio_opts = "-c:a copy"
                    print "[INFO]: Input Audio is already in %s format.Copying Audio" %(audio_codec)
                else:
                    default_audio_opts = ' -c:a '+av_codec["acodec"]
            else:
                print "[INFO]: Input Stream has no Audio. Skipping"
                default_audio_opts = ""

            transcoder_command = 'ffmpeg -i '+input_file+' '+ default_video_opts+' '+compression_opts+' '+default_audio_opts+' '+output_file
            print transcoder_command
            os.system(transcoder_command)

        elif encoding_type == "2-Pass":
            output_file = basefilepath + '_H265_2pass' + extension

            if av_info["vrate"] != None:
                video_bitrate_info = '-b:v '+av_info["vrate"]+' -maxrate '+av_info["max"]+' -minrate '+av_info["min"]+' -bufsize '+av_info["buf"]
            else:
                video_bitrate_info = ""
            if av_info["arate"] != None:
                audio_bitrate_info = ' -b:a '+av_info["arate"]
            else:
                audio_bitrate_info = ""

            if av_info["video_opts"] != None:
                video_opts = av_info["video_opts"]
            else:
                video_opts = ""
            if av_info["audio_opts"] != None:
                audio_opts = av_info["audio_opts"]
            else:
                audio_opts = ""

            default_video_opts = ' -c:v '+av_codec["vcodec"]+' '+video_opts+' '+video_bitrate_info
            if actual_audio_codec != []:
                default_audio_opts = ' -c:a '+av_codec["acodec"]+' '+audio_bitrate_info+' '+audio_opts
            else:
                default_audio_opts = ""

            pass1_command = 'ffmpeg -y -i '+input_file+' '+default_video_opts+' -x265-params pass=1 -an -f mp4 /dev/null'
            pass2_command = 'ffmpeg -i '   +input_file+' '+default_video_opts+' -x265-params pass=2 '+default_audio_opts+' '+output_file
            print(pass1_command)
            print(pass2_command)
            os.system(pass1_command)
            os.system(pass2_command)


    ###########################################################
    # Transcoding to H264 video codec
    ###########################################################
    if video_codec in ["H.264"]:
        output_file = basefilepath + '_H264' +audio_codec.upper()+ extension

        if encoding_type.lower() == "crf":
            if 'avc1' in actual_video_codec:
                default_video_opts = "-c:v copy"
                print "[INFO]: Input Video is already in H264 format.Copying Video"
            else:
                default_video_opts = ' -c:v '+av_codec["vcodec"]

            compression_opts = '-tag:v avc1 -crf '+comp_info["crf"]+' -preset '+comp_info["preset"]
            if actual_audio_codec != []:
                if audio_codec.lower() in actual_audio_codec:
                    default_audio_opts = "-c:a copy"
                    print "[INFO]: Input Audio is already in %s format.Copying Audio" %(audio_codec)
                else:
                    default_audio_opts = ' -c:a '+av_codec["acodec"]
            else:
                print "[INFO]: Input Stream has no Audio. Skipping"
                default_audio_opts = ""

            transcoder_command = 'ffmpeg -i '+input_file+' '+ default_video_opts+' '+compression_opts+' '+default_audio_opts+' '+output_file
            print transcoder_command
            os.system(transcoder_command)

        elif encoding_type == "2-Pass":
            output_file = basefilepath + '_H264_2pass' + extension

            if av_info["vrate"] != None:
                video_bitrate_info = '-b:v '+av_info["vrate"]+' -maxrate '+av_info["max"]+' -minrate '+av_info["min"]+' -bufsize '+av_info["buf"]
            else:
                video_bitrate_info = ""
            if av_info["arate"] != None:
                audio_bitrate_info = ' -b:a '+av_info["arate"]
            else:
                audio_bitrate_info = ""

            if av_info["video_opts"] != None:
                video_opts = av_info["video_opts"]
            else:
                video_opts = ""
            if av_info["audio_opts"] != None:
                audio_opts = av_info["audio_opts"]
            else:
                audio_opts = ""

            default_video_opts = ' -c:v '+av_codec["vcodec"]+' '+video_opts+' '+video_bitrate_info

            if actual_audio_codec != []:
                default_audio_opts = ' -c:a '+av_codec["acodec"]+' '+audio_bitrate_info+' '+audio_opts
            else:
                default_audio_opts = ""

            pass1_command = 'ffmpeg -y -i '+input_file+' '+default_video_opts+' -x264-params pass=1 -an -f mp4 /dev/null'
            pass2_command = 'ffmpeg -i '   +input_file+' '+default_video_opts+' -x264-params pass=2 '+default_audio_opts+' '+output_file
            print(pass1_command)
            print(pass2_command)
            os.system(pass1_command)
            os.system(pass2_command)


    ###########################################################
    # Transcoding to VP9 video codec
    ###########################################################
    if video_codec in ["VP9"]:
        output_file = basefilepath + '_VP9_'+audio_codec.upper()+'.webm'

        if encoding_type == "2-Pass":

            if av_info["vrate"] != None:
                video_bitrate_info = '-b:v '+av_info["vrate"]+' -maxrate '+av_info["max"]+' -minrate '+av_info["min"]+' -bufsize '+av_info["buf"]
            else:
                video_bitrate_info = ""
            if av_info["arate"] != None:
                audio_bitrate_info = ' -b:a '+av_info["arate"]
            else:
                audio_bitrate_info = ""

            if av_info["video_opts"] != None:
                video_opts = av_info["video_opts"]
            else:
                video_opts = ""
            if av_info["audio_opts"] != None:
                audio_opts = av_info["audio_opts"]
            else:
                audio_opts = ""

            default_video_opts = ' -c:v '+av_codec["vcodec"]+' '+video_opts+' '+video_bitrate_info
            #default_video_opts = video_opts + " -tile-columns 2 -g 240 -threads 8 -quality good " + " -c:v libvpx-vp9 "

            if actual_audio_codec != []:
                default_audio_opts = ' -c:a '+av_codec["acodec"]+' '+audio_bitrate_info+' '+audio_opts
            else:
                default_audio_opts = ""

            vp9_pass1_command = 'ffmpeg -i '+input_file+' '+default_video_opts+' '+default_audio_opts+' -pass 1 -speed 1 '+output_file
            vp9_pass2_command = 'ffmpeg -i '+input_file+' '+default_video_opts+' '+default_audio_opts+' -pass 2 -speed 1 '+output_file
            print(vp9_pass1_command)
            print(vp9_pass2_command)
            os.system(vp9_pass1_command)
            os.system(vp9_pass2_command)

    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back(output_file)



def up_down_scaler(input_file,scaling_info,av_codec,av_info,comp_info):
    basefilepath, extension = os.path.splitext(input_file)
    output_file = basefilepath + '_' + scaling_info["selected_resolution"] + extension


    res = scaling_info["selected_resolution"]
    if scaling_info["scaling_opts"] != None:
        scaling_opts = scaling_info["scaling_opts"]
    else:
        scaling_opts = ""

    if av_info[res]["vrate"] != None:
        video_bitrate_info = '-b:v '+av_info[res]["vrate"]+' -maxrate '+av_info[res]["max"]+' -minrate '+av_info[res]["min"]+' -bufsize '+av_info[res]["buf"]
    else:
        video_bitrate_info = ""
    if av_info[res]["arate"] != None:
        audio_bitrate_info = ' -b:a '+av_info[res]["arate"]
    else:
        audio_bitrate_info = ""

    if av_info[res]["video_opts"] != None:
        video_opts = av_info[res]["video_opts"]
    else:
        video_opts = ""
    if av_info[res]["audio_opts"] != None:
        audio_opts = av_info[res]["audio_opts"]
    else:
        audio_opts = ""

    default_video_opts = ' -c:v '+av_codec["vcodec"]+' '+video_opts+' '+video_bitrate_info
    default_audio_opts = ' -c:a '+av_codec["acodec"]+' '+audio_bitrate_info+' '+audio_opts


    if scaling_info["scaling_method"] == "CRF Only":
       scaling_command = ' -vf '+scaling_info["scaling_resolution"]+' '+scaling_opts+' -crf '+comp_info["crf"]+' -preset '+comp_info["preset"]
    else:
       compression_opts = '-preset ' + comp_info["preset"] + ' ' + comp_info["keyint"]

       scaling_command = ' -vf '+scaling_info["scaling_resolution"]+' '+scaling_opts+' '+default_video_opts+' '+compression_opts+' '+default_audio_opts

    scaler_command = 'ffmpeg -i '+input_file + scaling_command+' '+output_file
    print scaler_command
    os.system(scaler_command)
    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back(output_file)



def hls_stream_generator(input_file,selected_resolutions,av_codec,av_info,comp_info):

    counter = 1
    split_info = ""
    scale_info = ""
    stream_command = ""
    vmap_commands = []
    amap_commands = []
    res_scale_info = {"2160":"scale=w=3840:h=2160","1080":"scale=w=1920:h=1080","720":"scale=w=1280:h=720",
                      "480":"scale=w=854:h=480","360":"scale=w=640:h=360" }

    for res in selected_resolutions:
        index = str(counter - 1)
        output_counter = str(counter)
        output_instance = "[v"+str(counter)+"]"
        split_info = split_info + output_instance
        if stream_command != "":
            stream_command = stream_command + " "
        stream_command = stream_command + "v:"+index+",a:"+index
        if scale_info != "":
            scale_info = scale_info +"; "
        scale_info = scale_info + output_instance + res_scale_info[res] + "[v"+output_counter+"out]"


        compression_opts = '-preset ' + comp_info["preset"] + ' ' + comp_info["keyint"]
        video_opts = '"'+av_info[res]["video_opts"]+'"'

        vmap_command = '-map '+'[v'+output_counter+'out]'+' -c:v:'+index+' '+av_codec["vcodec"]+' '+video_opts+' -b:v:'+index+' '+av_info[res]["vrate"] +' -maxrate:v:'+index+' '+ av_info[res]["max"]+' -minrate:v:'+index+' '+av_info[res]["min"]+' -bufsize:v:'+index+' '+av_info[res]["buf"]+' '+compression_opts
        vmap_commands.append(vmap_command)
        amap_command = '-map a:0 -c:a:'+index+' '+av_codec["acodec"]+' -b:a:'+index+' '+av_info[res]["arate"]+' '+av_info[res]["audio_opts"]
        amap_commands.append(amap_command)

        counter += 1

    split_info = '[0:v]split='+str(len(selected_resolutions))+split_info+'; '
    stream_command = '"'+stream_command+'"'
    filter_options = '-filter_complex "'+split_info+' '+scale_info+'" '
    generate_command = " ".join(['ffmpeg', '-i', input_file] + filter_options.split())

    vmap_commands_all = " ".join(vmap_commands)
    amap_commands_all = " ".join(amap_commands)

    hls_stream_gen_command = '-f hls -hls_time 2 -hls_playlist_type vod -hls_flags independent_segments -hls_segment_type mpegts -hls_segment_filename stream_%v/data%02d.ts -master_pl_name master.m3u8 -var_stream_map ' + stream_command+' stream_%v.m3u8'

    final_hls_gen_command = generate_command+" "+vmap_commands_all+" "+amap_commands_all+" "+hls_stream_gen_command

    print(final_hls_gen_command)
    os.system(final_hls_gen_command)
    for index in range(0,len(selected_resolutions)):
        stream_id = "stream_"+str(index)
        replace_cmd  = "sed -i 's/data/"+stream_id+"\/data/g' "+stream_id+".m3u8"
        os.system(replace_cmd)
    play_option = raw_input("\nDo you want to play the generated stream?[Y/N]: ")
    if str(play_option) == 'Y':
        start_play_back("master.m3u8")




def hls_stream_data_collector():
    print ("\n#--------------HLS Stream Generator----------------#")
    # Choose the codecs required
    print ("Choose Video & Audio Codecs")
    print ("Video: 1. H.264 / 2. H.265")
    print ("Audio: 1. AAC / 2.AC3(DD) / 3.EAC3(dolby digital plus)")
    video_codecs = {"1":"H.264","2":"H.265"}
    audio_codecs = {"1":"AAC","2":"AC3","3":"EAC3"}
    video_codec_libs = {"1":"libx264 -x264-params","2":"libx265 -x265-params"}
    audio_codec_libs = {"1":"aac","2":"ac3","3":"eac3"}
    av_codec = {"vcodec":"","acodec":""}

    video_codec_id = str(input("Enter video codec id: "))
    audio_codec_id = str(input("Enter audio codec id: "))
    if str(video_codec_id).strip() == "":
        video_codec = "H.264"
        av_codec["vcodec"] = video_codec_libs.get("1")
    else:
        video_codec = video_codecs.get(video_codec_id)
        av_codec["vcodec"] = video_codec_libs.get(video_codec_id)

    if str(audio_codec_id).strip() == "":
        audio_codec = "AAC"
        av_codec["acodec"] = audio_codec_libs.get("1")
    else:
        audio_codec = audio_codecs.get(audio_codec_id)
        av_codec["acodec"] = audio_codec_libs.get(audio_codec_id)

    # Choose the required resolutions
    print("Choose the required resolutions")
    print("1. 2160(4K), 2. 1080(HD), 3.720, 4.480(SD), 5.360")
    standard_resolutions = ["2160","1080","720","480","360"]
    input_resolutions = str(raw_input("Select the resoltions: "))

    selected_resolutions = []
    if "-" in input_resolutions:
        n1 = int(input_resolutions.split("-")[0])
        n2 = int(input_resolutions.split("-")[1])
        for index in range(n1,n2+1):
            selected_resolutions.append(standard_resolutions[index-1])
    elif "," in input_resolutions:
        for index in input_resolutions.split(","):
            selected_resolutions.append(standard_resolutions[index-1])
    else:
        index = int(input_resolutions)
        selected_resolutions.append(standard_resolutions[index-1])

    print("Resolutions selected for HLS stream: ", selected_resolutions)

    print("Going to generate HLS " + video_codec + "_" +audio_codec + " stream...")
    get_default_opts(video_codec,audio_codec)
    av_info = {}
    for res in selected_resolutions:
        av_info[res] = {"vrate":"","min":"","max":"","buf":"","video_opts":"","arate":"","audio_opts":""}

    generation_options = raw_input("\nDo you want to provide AV bitrates, channel, preset options[Y/N]?: ")
    comp_info = {"preset":"","keyint":""}

    if str(generation_options) == "Y":
        # 1. Get the present and keyframe length inputs from the user
        # If user presses ENTER, use the default values
        preset_opt = raw_input("Default preset slow. Override with new preset ?: ")
        if preset_opt.strip() != "":
            comp_info["preset"] = preset_opt
        else:
            comp_info["preset"] = default_compression_opts["preset"]

        keyframe_opt = raw_input("Default length 48. Override with new length ?: ")
        if str(keyframe_opt).strip() != "":
            comp_info["keyint"] = "-g " + str(keyframe_opt) + " -sc_threshold 0 -keyint_min " + str(keyframe_opt)
        else:
            comp_info["keyint"] = default_compression_opts["keyint"]

        # 2. Get the AV bitrates, channel, profile or other inputs from the user
        # If user presses ENTER, use the default values
        print("Enter AV bitrates/profile/channel options if any...")
        for res in av_info.keys():
            # 1. Get the Video bitrate inputs from the user for each resolution
            video_bitrate_opts = raw_input("\n[%s]: video bitrate, min, max, bufsize: "%(res))
            if video_bitrate_opts.strip() != "":
                vrate,min,max,buf = video_bitrate_opts.split()
            else:
                vrate,min,max,buf = [default_bitrate_opts[res]["vrate"],default_bitrate_opts[res]["min"],default_bitrate_opts[res]["max"],default_bitrate_opts[res]["buf"]]

            av_info[res]["vrate"] =vrate
            av_info[res]["min"]  =min
            av_info[res]["max"]  =max
            av_info[res]["buf"]  =buf

            # 2. Get the Video option inputs from the user for each resolution
            video_opts = raw_input("[%s]: video options if any: "%(res))
            if video_opts.strip() == "":
                video_opts = default_bitrate_opts[res]["video_opts"]
            av_info[res]["video_opts"] = video_opts

            # 3. Get the Audio bitrate inputs from the user for each resolution
            audio_bitrate_opts = raw_input("[%s]: audio bitrate: "%(res))
            if audio_bitrate_opts != "":
                arate = audio_bitrate_opts
            else:
                arate = default_bitrate_opts[res]["arate"]
            av_info[res]["arate"] = arate

            # 4. Get the Audio option inputs from the user for each resolution
            audio_opts = raw_input("[%s]: audio options if any: "%(res))
            if audio_opts.strip() == "":
                audio_opts = default_bitrate_opts[res]["audio_opts"]
            av_info[res]["audio_opts"] = audio_opts

    else:
        comp_info["preset"] = default_compression_opts["preset"]
        comp_info["keyint"] = default_compression_opts["keyint"]
        for res in av_info.keys():
            vrate,min,max,buf = [default_bitrate_opts[res]["vrate"],default_bitrate_opts[res]["min"],default_bitrate_opts[res]["max"],default_bitrate_opts[res]["buf"]]

            av_info[res]["vrate"] =vrate
            av_info[res]["min"]  =min
            av_info[res]["max"]  =max
            av_info[res]["buf"]  =buf
            av_info[res]["video_opts"] = default_bitrate_opts[res]["video_opts"]
            av_info[res]["arate"] = default_bitrate_opts[res]["arate"]
            av_info[res]["audio_opts"] = default_bitrate_opts[res]["audio_opts"]

    print av_info
    hls_stream_generator(sys.argv[1],selected_resolutions,av_codec,av_info,comp_info)


def transcoder_data_collector():
    print ("\n#-------------- TRANSCODER ----------------#")
    # 1. Choose the Transcoding method
    print("Choose the transcoding method")
    print("1. CRF (Constant rate factor)")
    print("2. 2-Pass Encoding")
    transcoding_methods = ["CRF","2-Pass"]
    input_transcoding_method = int(raw_input("Enter transcoding Id: "))
    selected_transcoding_method = transcoding_methods[input_transcoding_method-1]

    comp_info = {"preset":"","keyint":"","crf":""}
    av_codec  = {"vcodec":"","acodec":""}
    video_codecs = {"1":"H.264","2":"H.265","3":"VP9"}
    audio_codecs = {"1":"AAC","2":"AC3","3":"EAC3","4":"OPUS"}
    video_codec_libs = {"1":"libx264","2":"libx265","3":"libvpx-vp9"}
    audio_codec_libs = {"1":"aac","2":"ac3","3":"eac3","4":"libopus"}
    actual_video_codec = get_codec_info(sys.argv[1], 'v:0')[0]
    actual_audio_codec = get_codec_info(sys.argv[1], 'a:0')[0]
    av_info = {"vrate":"","min":"","max":"","buf":"","video_opts":"","arate":"","audio_opts":""}
    print("Actual Video codec: %s , Audio codec: %s" %(actual_video_codec,actual_audio_codec))

    print ("Video: 1. H.264, 2. H.265, 3.VP9 ")
    print ("Audio: 1. AAC , 2.AC3(DD) , 3.EAC3(dolby digital plus), 4.OPUS")
    print ("Choose Video & Audio Codecs")
    video_codec_id = str(input("Enter video codec id: "))
    audio_codec_id = str(input("Enter audio codec id: "))
    av_codec["vcodec"] = video_codec_libs.get(video_codec_id)
    av_codec["acodec"] = audio_codec_libs.get(audio_codec_id)
    av_codec["vcodec_name"] = video_codecs.get(video_codec_id)
    av_codec["acodec_name"] = audio_codecs.get(audio_codec_id)


    # 1. Get the preset inputs from the user
    # If user presses ENTER, use the default values
    preset_opt = raw_input("Default preset slow. Override with new preset ?: ")
    if preset_opt.strip() != "":
        comp_info["preset"] = preset_opt
    else:
        comp_info["preset"] = default_compression_opts["preset"]
    if selected_transcoding_method == "CRF":
        # 1. Get the CRF and preset inputs from the user
        # If user presses ENTER, use the default values
        crf_opt = raw_input("Default crf 18. Override with new value?: ")
        if crf_opt.strip() != "":
            comp_info["crf"] = crf_opt
        else:
            comp_info["crf"] = default_compression_opts["crf"]

        comp_info["keyint"] = None

    else:
        # 1. Get the keyframe length inputs from the user
        # If user presses ENTER, use the default values
        keyframe_opt = raw_input("Default length 48. Override with new length ?: ")
        if str(keyframe_opt).strip() != "":
            comp_info["keyint"] = "-g " + str(keyframe_opt) + " -sc_threshold 0 -keyint_min " + str(keyframe_opt)
        else:
            comp_info["keyint"] = default_compression_opts["keyint"]

        generation_options = raw_input("\nDo you want to provide AV bitrates,channel,options[Y/N]?: ")
        if str(generation_options) == 'Y':
            # 1. Get the Video bitrate inputs from the user for each resolution
            video_bitrate_opts = raw_input("\nvideo bitrate, min, max, bufsize: ")
            if video_bitrate_opts.strip() != "":
                vrate,min,max,buf = video_bitrate_opts.split()
            else:
                vrate,min,max,buf = [None,None,None,None]

            av_info["vrate"] =vrate
            av_info["min"]  =min
            av_info["max"]  =max
            av_info["buf"]  =buf

            # 2. Get the Video option inputs from the user for each resolution
            video_opts = raw_input("\nvideo options if any: ")
            if video_opts.strip() == "":
                video_opts = None
            av_info["video_opts"] = video_opts

            # 3. Get the Audio bitrate inputs from the user for each resolution
            audio_bitrate_opts = raw_input("\naudio bitrate: ")
            if audio_bitrate_opts != "":
                arate = audio_bitrate_opts
            else:
                arate = None
            av_info["arate"] = arate

            # 4. Get the Audio option inputs from the user for each resolution
            audio_opts = raw_input("\naudio options if any: ")
            if audio_opts.strip() == "":
                audio_opts = None
            av_info["audio_opts"] = audio_opts
        else:
            av_info["vrate"] =None
            av_info["min"]   =None
            av_info["max"]   =None
            av_info["buf"]   =None
            av_info["video_opts"] = None
            av_info["arate"] = None
            av_info["audio_opts"] = None

    transcoder(sys.argv[1],av_codec,av_info,comp_info,selected_transcoding_method)  


def main():
    print("########################################################")
    print("FFMPEG Based PyTool For AV Processing                   ")
    print("########################################################")
    print("Supported Features:")
    print("1.HLS Stream Generation")
    print("2.Up/Down Scaler")
    print("3.Transcoder")
    print("4.AV MUX/DEMUX")
    print("5.AV Processing")
    user_option = int(input("\nSelect operation to continue: "))
    if(user_option == 1):
        hls_stream_data_collector();
    elif(user_option == 2):
        up_down_scaler_data_collector();
    elif(user_option == 3):
        transcoder_data_collector();
    elif(user_option == 4):
        mux_demux_data_collector();
    elif(user_option == 5):
        processing_data_collector();


if __name__== "__main__" :
    main()


