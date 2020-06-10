activity_codes = {
    "1":" ROI 1",
    "2":" ROI 2",
    "3": "ROI 3",
    "4": "ROI 4",
    "5": "ROI 5",
    "6": "ROI 6",
    "7": "ROI 7",
    "8": "ROI 8",
    "9": "ROI 9",
    "10" : "ROI 10",
    "11": "ROI 11",
    "12": "ROI 12",
    "13": "ROI 13",
    "14": "ROI 14",
    "15": "ROI 15",
    "16": "ROI 16",
    "17": "ROI 17",
    "18": "ROI 18",
    "19": "ROI 19",
    "20": "ROI 20",
    "21": "ROI 21",
    "22": "ROI 22"
    }

document.body.style.zoom="70%"

function create_visualization(id,activityDictionary) {
    radians = 0.0174532925,
    vizRadius = 350,
    margin = 100,
    width = (vizRadius+margin)*2 ,
    height = (vizRadius+margin)*2,

    activityCodes = Object.keys(activityDictionary)
    numCategories = activityCodes.length


    var codesScale = d3.scaleLinear()
    .range([0,360])
    .domain([0,numCategories-1]);

    fociGroups = {}
    for(i=0;i<numCategories;i++){
        fociGroups[activityCodes[i]]={}
        if(i==0){
           fociGroups[activityCodes[i]]['x']=0
           fociGroups[activityCodes[i]]['y']=0
        }
        else{
            fociGroups[activityCodes[i]]['x']= (vizRadius-80)*Math.sin(codesScale(i-1)*radians);
            fociGroups[activityCodes[i]]['y']= -(vizRadius-80)*Math.cos(codesScale(i-1)*radians);
        }
    }

    svg = d3.select("#"+id).
    append("svg").
    attr("width",width).
    attr("height",height)
    vizGroup = svg.append("g").
                attr("id","viz-area").
                attr("transform",`translate(${vizRadius+margin},${vizRadius+margin})`)


    vizGroup.selectAll('.second-label')
        .data(activityCodes)
            .enter()
            .append('text')
            .attr('class',"second-label")
            .attr('text-anchor','middle')
            .attr('x',function(d,i){
                if(i==0){
                    return 0;
                }
                return vizRadius*Math.sin(codesScale(i-1)*radians);
            })
            .attr('y',function(d,i){
                if(i==0){
                    return 0;
                }
                return -vizRadius*Math.cos(codesScale(i-1)*radians) ;
            })
            .attr('z',100)
            .html(function(d,i){
                 if(i==0){
                    return `<tspan x="0" y="0"  z="100">${activityDictionary[d]}</tspan>
                        <tspan class="${"perc"+activityCodes[i]}" x="0" y="0", dy="1.5em" ">${i}%</tspan>`;
                }
                return `<tspan x="${vizRadius*Math.sin(codesScale(i-1)*radians)}" y="${-vizRadius*Math.cos(codesScale(i-1)*radians)}"  z="100">${activityDictionary[d]}</tspan>
                        <tspan class="${"perc"+activityCodes[i]}" x="${vizRadius*Math.sin(codesScale(i-1)*radians)}" y="${-vizRadius*Math.cos(codesScale(i-1)*radians)}" dy=1em  z="100" >${i}%</tspan>`;
            });

    // for(i=0;i<numCategories;i++){
    //     vizGroup.append('circle').
    //         attr('cx',fociGroups[activityCodes[i]]['x']).
    //         attr('cy',fociGroups[activityCodes[i]]['y']).
    //         attr('r',10)

    // }


    // force animation code



    function color(id){
        if(id==50){
            id=19
        }
        val = id/19
        return d3.interpolateRainbow(val);

    }

    var node = vizGroup
            .selectAll(".people")
            .data(processed_data_arr,d => d.key)
            .enter().append("circle")
            .attr("r", 3)
            .attr("fill", (d)=>color(+d['activity'][d.current_activity].activity_code));

    var forceX = d3.forceX((d) => fociGroups[d['activity'][d.current_activity].activity_code].x);//fociGroups[d['activity'][d.current_activity].activity_code].x);
    var forceY = d3.forceY((d) => fociGroups[d['activity'][d.current_activity].activity_code].y);

    var force = d3.forceSimulation(processed_data_arr)
    .velocityDecay(0.65)
    .force('x', forceX)
    .force('y', forceY)
    .force("collide", d3.forceCollide(3));

    force.nodes(processed_data_arr)
    .on('tick', function() {
         node
            .attr('transform', (d) => {
                return 'translate(' + (d.x) + ',' + (d.y) + ')';
            });
        });

    function pad(d) {
        return (d < 10) ? '0' + d.toString() : d.toString();
    }

    d3.interval(function(){
        time = (time+1)% 60
        hour = Math.floor(time/60)

        minutes = time - hour*60
        if(hour>12 && hour < 24){
            hour = hour-12
            d3.select("#time").text(pad(hour)+":"+pad(minutes) )//+" a.m."
        }
        else{
            hour = hour%24
            d3.select("#time").text(pad(hour)+":"+pad(minutes))//+" p.m." 

        }

        percentage_counts = {}
        processed_data_arr.forEach(function(d){
            if(time == 20){
                d.current_activity=1
            }
            else if(d.current_activity==0){
                    //le
            }
            else if(+d['activity'][d.current_activity]["stop"] < time){
                d.current_activity = (d.current_activity+ 1)% d.activity.length
                if(d.current_activity==0){
                    console.log(1)
                }
            }

            //count percentage of each activity
            if( percentage_counts[d['activity'][d.current_activity].activity_code] == undefined){
                percentage_counts[d['activity'][d.current_activity].activity_code]=1
            }
            else{
                percentage_counts[d['activity'][d.current_activity].activity_code] += 1
            }

        })
        for(var i =0;i<activityCodes.length;i++){
                val = percentage_counts[activityCodes[i]]
                if(val == undefined){
                    val =0
                }
                val = val/10
                val = Math.floor(val*100)/100
                d3.select(".perc"+activityCodes[i]).text(val+"%")
        }
        node.transition().duration(0).attr("fill", (d)=>color(d['activity'][d.current_activity].activity_code));
        force.nodes(processed_data_arr);
        force.alpha(0.8).restart();
    },100)


    vizGroup.selectAll('.second-label').raise()
}

time = 1

processed_data = {}

d3.csv('http://localhost:5000/bubblecsv', function(data) {
    if(processed_data[data["TUCASEID"]] === undefined){
        processed_data[data["TUCASEID"]] = {}
        processed_data[data["TUCASEID"]]["activity"] = [{
                                                                    "start": 20,
                                                                    "stop": 20,
                                                                    "activity_code": 0
                                                                }]
        processed_data[data["TUCASEID"]]["current_activity"] = 1
    }
    activity_id = data["TUACTIVITY_N"].toString()
    processed_data[data["TUCASEID"]]["activity"][activity_id] = {
                                                                    "start": data["start_minute"],
                                                                    "stop": data["stop_minute"],
                                                                    "activity_code": data["TUTIER1CODE"]
                                                                }


}).then(start);


function start(){
processed_data_arr = []

keys = Object.keys(processed_data)
for(var i=0;i<keys.length;i++){
    dat = processed_data[keys[i]]
    dat["key"] = keys[i]
    processed_data_arr.push(dat)
}


create_visualization("Visualization",activity_codes)
}
