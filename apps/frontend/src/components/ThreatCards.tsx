import {CrisisEvent} from "@/types/crisis";


export default function ThreatCard({
event
}:{
event:CrisisEvent
}){


const colors={

low:
"from-green-900 to-green-500",

moderate:
"from-yellow-900 to-yellow-500",

high:
"from-orange-900 to-orange-500",

critical:
"from-red-950 to-red-500"

};



return (

<div

className={`
absolute
right-8
top-8
w-96
rounded-2xl
p-6
text-white
bg-gradient-to-br
${colors[event.severity]}
shadow-2xl
z-[1000]

transition-all
duration-500
`}

>


<h2 className="text-xl font-bold">

⚠ {event.severity.toUpperCase()} RISK

</h2>


<h3 className="mt-3 text-lg">

{event.title}

</h3>


<p className="opacity-80">

{event.location}

</p>



<div className="mt-5">

Risk Score:

<b>
 {event.riskScore}/100
</b>

</div>



<p className="mt-4">

{event.summary}

</p>



<p className="mt-4">

AI Confidence:
<b>
 {event.confidence}%
</b>

</p>



</div>

)

}