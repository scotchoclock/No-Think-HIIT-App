import json, re

CUES = {
 "Bodyweight squats": ["Feet shoulder-width, sit your hips back and down", "Chest tall, drive through your heels", "Keep your knees tracking over your toes"],
 "Arm circles": ["Big, slow circles, reaching long through your fingertips", "Keep your shoulders relaxed and your chest open", "Smooth and easy, then switch directions"],
 "Jumping jacks": ["Land softly on the balls of your feet", "Arms all the way up, feet wide", "Stay light and springy, and keep a steady rhythm"],
 "Torso twists": ["Rotate from your middle and let your arms hang loose", "Keep your hips quiet and your chest proud", "Nice and easy, breathe as you twist"],
 "Leg swings": ["Hold something steady and swing the leg front to back", "Keep your core tight and your hips level", "Loose and easy, then switch legs"],
 "Push-ups": ["Hands under your shoulders, body in one long line", "Lower your chest, then press the floor away", "Squeeze your glutes and keep your core tight"],
 "Burpees": ["Chest to the floor, then explode up", "Land soft and keep your breath moving", "Find a steady rhythm, no need to rush"],
 "Incline push-ups": ["Hands on a sturdy surface, body in a straight line", "Lower your chest to the edge, then press back", "Keep your elbows at about forty-five degrees"],
 "Diamond push-ups": ["Hands together under your chest, forming a diamond", "Elbows tucked close, lower with control", "Press up strong and keep your hips level"],
 "Pike push-ups": ["Hips high, head moving between your hands", "Lower the top of your head toward the floor", "Press back up and keep your legs long"],
 "Tricep dips": ["Hands on the edge, bend your elbows back, close to your body", "Keep your chest lifted and your shoulders down", "Lower with control, then press up tall"],
 "Bent-over dumbbell rows": ["Hinge at the hips and keep your back flat", "Pull your elbows back, close to your ribs", "Squeeze your shoulder blades together at the top"],
 "Dumbbell thrusters": ["Squat deep, then drive up and press overhead", "Use your legs to power the press", "Keep the weights close and your core tight"],
 "Dumbbell shoulder press": ["Weights at shoulder height, then press them overhead", "Keep your ribs down and your core tight", "Lower slowly, then drive up again"],
 "Dumbbell floor press": ["Lie back with your elbows at forty-five degrees", "Press the weights up over your chest", "Lower slowly until your arms touch the floor"],
 "Dumbbell curl to press": ["Curl up, rotate, and press overhead", "Keep your elbows close to your body", "Smooth and steady, don't swing the weights"],
 "Dumbbell hammer curls": ["Palms facing in, curl toward your shoulders", "Keep your elbows pinned to your sides", "Lower slowly and don't swing"],
 "Dumbbell lateral raises": ["Raise your arms out to the sides, up to shoulder height", "Lead with your elbows, not your hands", "Lower slowly and keep your shoulders down"],
 "Mountain climbers": ["Shoulders over your wrists, drive your knees in", "Keep your hips low and your core tight", "Quick feet and a steady breath"],
 "Plank shoulder taps": ["Feet wide, tap one shoulder, then the other", "Keep your hips quiet and don't let them rock", "Brace your core and keep breathing"],
 "High knees": ["Drive your knees up to hip height", "Pump your arms and stay light on your feet", "Tall chest and quick feet"],
 "Bear crawl holds": ["Knees an inch off the floor and your back flat", "Press into your hands and keep your core tight", "Breathe steady and don't let your hips rise"],
 "Plank hold": ["Forearms down, body in one long line", "Squeeze your glutes and your core", "Push the floor away and keep your hips level"],
 "Side plank holds": ["Stack your feet and lift your hips high", "Press into your forearm and stay long", "Breathe slowly and keep your hips lifted"],
 "Russian twists": ["Lean back a little, chest proud", "Rotate your whole torso from side to side", "Tap the floor beside you each time"],
 "Flutter kicks": ["Lower back pressed into the floor", "Small, quick kicks with your legs long", "Keep your core tight and your neck relaxed"],
 "Bicycle crunches": ["Opposite elbow to opposite knee", "Slow and controlled, no yanking your neck", "Extend the other leg all the way out"],
 "Dead bugs": ["Lower back glued to the floor", "Opposite arm and leg, nice and slow", "Breathe out as you reach"],
 "Superman holds": ["Squeeze your glutes and lift your arms and legs", "Look at the floor and keep your neck long", "Breathe steady and hold it strong"],
 "Renegade rows": ["Wide feet, brace hard, row one elbow back", "Keep your hips level with the floor", "Squeeze your shoulder blade and lower slowly"],
 "Dumbbell suitcase carries": ["Stand tall and don't lean to the side", "Shoulders level, core tight, walk steady", "Smooth, even steps and an easy breath"],
 "Reverse lunges": ["Step back and lower your back knee toward the floor", "Keep your chest tall and your front heel planted", "Drive through the front foot to stand"],
 "Jumping lunges": ["Switch legs in the air and land soft", "Keep your chest up and your core tight", "Quick and light, find the rhythm"],
 "Jump squats": ["Swing your arms to help you jump", "Land softly through your whole foot", "Reset your stance before the next jump"],
 "Curtsy lunges": ["Step back and across, like a curtsy", "Keep your chest tall and your hips level", "Drive through the front heel to stand"],
 "Lateral lunges": ["Step wide to the side and sit back into that hip", "Keep the other leg straight, toes forward", "Push off the bent leg to come back"],
 "Single-leg glute bridges": ["Heel close to your hips, drive up through it", "Lift one leg and keep your hips level", "Squeeze your glute at the top"],
 "Broad jumps": ["Swing your arms and jump forward as far as you can", "Land softly with your knees bent", "Reset, then jump again"],
 "Dumbbell goblet squats": ["Hold the weight at your chest, then sit back and down", "Keep your chest proud and your elbows inside your knees", "Drive up through your heels"],
 "Dumbbell reverse lunges": ["Step back with control and lower the back knee", "Hold the weights close, chest tall", "Alternate legs, smooth and controlled"],
 "Weighted step-back lunges": ["Step back softly and lower with control", "Keep your torso tall and your front knee steady", "Press through the front foot to come back up"],
 "Dumbbell deadlifts": ["Hinge at the hips with the weights close to your legs", "Keep your back flat and your chest proud", "Stand tall and squeeze your glutes at the top"],
 "Dumbbell swings": ["Hike the weight back, then snap your hips forward", "Let your hips do the work, not your arms", "Keep your back flat and your core tight"],
 "Dumbbell Romanian deadlifts": ["Soft knees and hips back, feel it in your hamstrings", "Keep the weights close and your back flat", "Squeeze your glutes to stand tall"],
 "Single-leg deadlifts": ["Hinge forward and send the back leg behind you", "Keep both hips level and your back flat", "Soft knee on the standing leg, eyes on the floor ahead"],
 "Cossack squats": ["Feet wide, sink deep into one side", "Keep the other leg straight, toes up", "Chest tall, then switch to the other side"],
}
OPEN = ["Up next: {n}!", "Next up, {n}!", "Alright, {n}!", "Coming up, {n}!", "Time for {n}!", "Get ready for {n}!"]
NAMEONLY = [["Up next: {n}!", "Next up, {n}!"], ["Alright, {n}!", "Coming up, {n}!"]]
LEADS = ["Keep it smooth.", "Stay with it.", "Nice, and remember,"]

def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def lc(s): return s[0].lower()+s[1:]

clips=[]
def add(id,cat,text,energy,ex=None):
    clips.append({"id":id,"cat":cat,"text":text,"energy":energy,**({"ex":ex} if ex else {})})

for ei,(name,cues) in enumerate(CUES.items()):
    sl=slug(name); n=name[0].upper()+name[1:] if name[0].islower() else name
    # shown name: lower-case after opener reads naturally for TTS
    nm = name if name[:9]=="Dumbbell " and False else name
    nlow = name[0].lower()+name[1:] if not name.startswith("Dumbbell") else name  # keep the 'Dumbbell' capital
    nlow = name  # TTS handles capitals fine
    o=lambda i: OPEN[(ei+i)%len(OPEN)].format(n=nlow)
    add(f"{sl}.i1","intro", f"{o(0)} {cues[0]}.","mid",sl)
    add(f"{sl}.i2","intro", f"{o(1)} {cues[1]}.","mid",sl)
    add(f"{sl}.i3","intro", f"{o(2)} {cues[2]}.","mid",sl)
    add(f"{sl}.i4","intro", f"{o(3)} {cues[0]}. {cues[2]}.","mid",sl)
    a=NAMEONLY[0][ei%2].format(n=nlow); b=NAMEONLY[1][(ei//2)%2].format(n=nlow)
    add(f"{sl}.n1","name",a,"mid",sl); add(f"{sl}.n2","name",b,"mid",sl)
    for j in range(3):
        c=cues[(j+1)%3]
        add(f"{sl}.r{j+1}","remind", f"{LEADS[j]} {lc(c) if LEADS[j].endswith(',') else c}.","mid",sl)

G = {
 "go":("high",["Here we go!","Let's move!","Time to work!","And go!","Start strong!","Let's get it!","Showtime. Let's go!","Alright, go!"]),
 "rest":("low",["Nice work. Shake it out, slow your breath.","Good one. Let your arms hang and breathe deep.","That's it. Easy breath, loosen up.","Rest now. Breathe in slow, breathe out slower.","Well done. Shake out your legs and settle your breath.","Nice. Drop your shoulders and take a deep breath.","Good effort. Catch your breath, you're doing great.","Smooth work. Let your heart rate settle.","Recover. Slow breath in through the nose, out through the mouth.","Easy now. Roll your shoulders and breathe."]),
 "half":("mid",["Halfway there. Stay smooth, keep breathing.","Halfway. Keep it clean, you've got this.","Right on track. Halfway done.","Half done. Stay tall and keep moving.","That's halfway. Stay strong, stay smooth.","Halfway! Keep the rhythm going, you're doing great."]),
 "final":("high",["Ten seconds. Close it out strong!","Ten to go. Give it everything!","Last ten. Push through!","Ten seconds left. You've got this!","Almost there. Ten seconds, make them count!","Final ten. Finish it off!"]),
 "count":("high",["Three. Two. One.","Three... two... one.","Three, two, one.","And three, two, one."]),
 "breakstart":("low",["That's a circuit down. Grab some water, shake out your legs, and breathe. You earned it.","Circuit complete. Take a drink, stretch it out, enjoy the break.","Nice work. That circuit's done. Water, deep breaths, loosen up.","One circuit done. Take your time, drink some water, let your legs recover.","Great circuit. Breathe deep, shake it out, and get a sip of water.","Circuit finished. Slow your breath and let your body reset."]),
 "breakend":("mid",["Almost time. Shake out your hands and take a deep breath.","Break's nearly up. Roll your shoulders and get ready.","Back to it soon. Take one more slow breath.","Get ready to go again. Stay loose and easy.","Last few seconds. Shake it out, you're ready."]),
 "warmupstart":("low",["Let's begin with a gentle warm-up. Nice and easy, get the body moving.","Warm-up time. Ease in, find your breath, and loosen up.","Welcome. Let's warm up slowly, nothing rushed.","Let's get started. Warm up easy and let your body wake up."]),
 "cooldown":("low",["That's the last of the work. Time to cool down. Stand tall, breathe slow, and stretch out your hamstrings and chest.","Cool-down time. Slow your breath, walk it out, and stretch your hamstrings and chest.","Nicely done. Now ease down. Deep breaths, long stretches, let your heart rate settle.","All the hard work is done. Cool down slowly and breathe."]),
 "complete":("mid",["And that's the workout. Great job today. Take a slow breath, and be proud of that one.","Done. You showed up and you worked. Well done.","Workout complete. Nice and strong. Enjoy that feeling.","That's a wrap. Great work today, really.","You did it. Take a deep breath, and have a great day."]),
 "test":("mid",["Voice is on. Let's have a great workout."]),
 "newmix":("mid",["Fresh mix. Here's what we've got.","New workout, new mix. Here we go.","Shuffled. Let's try this one."]),
}
for cat,(en,lines) in G.items():
    for i,t in enumerate(lines,1): add(f"g.{cat}.{i}",cat,t,en)

# sibilant collision check: word ending in s/z/x/sh/ch followed by word starting s/z/sh
bad=[]
for c in clips:
    words=re.findall(r"[A-Za-z'\-]+|[.,!?:;]+", c["text"])
    for a,b in zip(words,words[1:]):
        if not re.match(r"[A-Za-z]",b): continue
        if re.search(r"(s|z|x|sh|ch|ce|se|ze)$", a.lower()) and re.match(r"(s|z|sh|c[ei])", b.lower()):
            bad.append((c["id"],a,b,c["text"][:80]))
print(len(clips),"clips;", sum(len(c["text"]) for c in clips),"chars")
for b in bad: print("SIB?",b)
json.dump(clips,open("manifest.json","w"),indent=0)
