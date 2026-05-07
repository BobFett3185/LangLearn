A platform to learn languages by speaking using an agentic pipeline with memory and tooling rather than hardcoded learning paths 
like on duolingo. we also skip straight to speaking because that is the most practical way to learn a language



The app will work by having some LLM first teach you how to say some word or phrase 
The LLM will decide what to teach you based on a memory implemented in a db 
This way there is a unique learning path and not a hardcoded curriculum 

After the agent decides what to teach you to say, we will have an 11 labs text to speech agent 
say it out loud for you to hear, you can replay it and practice as you wish 

Then you will be asked to say it back, once you feel comfortable 

Then we use Groq speech to text which has translate and transcribe 
that information is passed back to the main orchestrator agent which 
then decides to reteach you completely by breaking down the phrase, specifying word meaning 
or maybe it decides to show you the audio again and make you say it again 

once you move on the cycle continues and the agents memory is continously updated

