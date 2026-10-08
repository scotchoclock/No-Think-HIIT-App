import json,re
clips=[]
def add(i,cat,t): clips.append({"id":i,"cat":cat,"text":t,"energy":"mid"})
FIN=["Ten seconds left. You've got this.","Ten to go. Keep it moving, you're nearly there.","Last ten seconds. Push through, you're almost there.",
 "Ten seconds. Give me everything you've got.","Almost there. Just ten more seconds.","Ten seconds to go. Keep breathing, keep moving.",
 "Final ten. Nice and strong, you're doing great.","Ten seconds left. Hold that form, finish it off."]
CNT=["Three. Two. One.","Three... two... one.","Three, two, one.","And three, two, one.","Three. Two. One. Go.","Here we go. Three, two, one."]
GO=["Here we go!","Let's move!","Time to work!","And go!","Let's get it!","Alright, go!","Let's go!","Go time!"]
HALF=["Halfway there. Stay smooth, keep breathing.","Halfway. Keep it clean, you've got this.","Right on track. Halfway done.","Half done. Stay tall and keep moving.","That's halfway. Stay steady, stay smooth.","Halfway! Keep the rhythm going, you're doing great."]
for n,l in enumerate(FIN,1): add(f"g.fin2.{n}","fin2",l)
for n,l in enumerate(CNT,1): add(f"g.cnt2.{n}","cnt2",l)
for n,l in enumerate(GO,1): add(f"g.go2.{n}","go2",l)
for n,l in enumerate(HALF,1): add(f"g.half2.{n}","half2",l)
# circuit-aware break lines: key k-of-N (circuits finished k of N total)
BRK={
 "1of3":["Circuit one done. Two to go. Grab some water, shake out your legs, and breathe.","First circuit finished, with two still to come. Take a drink and let your breath settle."],
 "2of3":["Two circuits down, one to go. Water, deep breaths, loosen up.","Second circuit done. Just one more left. Shake it out and breathe."],
 "3of3":["That's all three circuits done! Take a quick breather, then a short finisher.","Circuit three complete. That was the last one. Catch your breath, the finisher is next."],
 "1of6":["Circuit one done. Five to go. Grab some water, shake it out, and ease into it.","First circuit finished, with five still to come. Take a drink and breathe."],
 "2of6":["Two circuits down, four to go. Water, deep breaths, loosen up.","Second circuit done. Four more to come. Shake it out and breathe."],
 "3of6":["Three circuits done. That's lap one finished, and you're halfway there! Take a drink and breathe.","Lap one complete. Three circuits down, three to go. Water, deep breaths, you earned it."],
 "4of6":["Four circuits down, two to go. Lap two is going well. Take a drink and breathe.","Fourth circuit done. Two more to come. Shake out your legs and reset."],
 "5of6":["Five circuits down, just one to go. Grab some water and get ready for the last one.","Fifth circuit finished. One circuit left. Deep breath, you're nearly there."],
 "6of6":["Circuit six complete. That was the last one! Take a quick breather, then a short finisher.","That's every circuit done! Catch your breath, the finisher is next."],
}
for k,ls in BRK.items():
    for n,l in enumerate(ls,1): add(f"b.{k}.{n}","brk",l)
bad=[]
for c in clips:
    words=re.findall(r"[A-Za-z'\-]+|[.,!?:;]+", c["text"])
    for a,b in zip(words,words[1:]):
        if not re.match(r"[A-Za-z]",b): continue
        if re.search(r"(s|z|x|sh|ch|ce|se|ze)$", a.lower()) and re.match(r"(s|z|sh|c[ei])", b.lower()): bad.append((c["id"],a,b,c["text"][:70]))
print(len(clips),"clips"); [print("SIB?",b) for b in bad]
json.dump(clips,open("manifest2.json","w"),indent=0)
