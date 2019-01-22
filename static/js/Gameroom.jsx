import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import ReactCountdownClock from 'react-countdown-clock';
import SevenSegClock from "./SevenSegClock.jsx"

let BASE_URL = "localhost:5000";
let TICK_TIME = 5000;
let HINT_AUDIO_FILE = "Crash-Cymbal-1.wav";


export default class Gameroom extends Component {
    constructor(props){
        super(props);
        this.state = {
            hint_text: "",
            hint_exists: false,
            hint_timer: 0,

            time: 100,
            paused: false,
            gamestate: "unstarted"
        };
        this.checkServerState();
    }

    render() {
        let minutes = Math.floor(this.state.time / 60);
        let seconds = this.state.time % 60;
        if (this.state.gamestate === "unstarted")
        {
            return(
            <div className="Gameroom">
                <p> Please wait for the game to start. </p>
            </div>
            );
        }
        else if (this.state.gamestate === "completed")
        {
            return(
            <div className="Gameroom">
                <p> Congratulations!! You finished with {this.state.time} seconds left! </p>
            </div>
            );
        }
        else if (this.state.gamestate === "out_of_time")
        {
            return(
            <div className="Gameroom">
                <p> Oh No!! You ran out of time! </p>
            </div>
            );
        }
        else if (this.state.hint_exists)
        {
            let minutes = Math.floor(this.state.time / 60);
            let seconds = this.state.time % 60;
            let paddedMinutes = minutes.toString(10).padStart(4, "0");
            let paddedSeconds = seconds.toString(10).padStart(4, "0");
            return (
            <div className="Gameroom" style={{whiteSpace: "nowrap"}}>
                <SevenSegClock color="black" minuteCount={2} secondCount={2} minutes={minutes} seconds={seconds}/>
                <p> Hint: {this.state.hint_text} </p>
            </div>
            );
        }
        else
        {
            return (
            <div className="Gameroom" style={{whiteSpace: "nowrap"}}>
                <SevenSegClock color="black" minuteCount={2} secondCount={2} minutes={minutes} seconds={seconds}/>
            </div>
            );
        }
    }

    checkServerState()
    {
        axios.get(`http://${BASE_URL}/getdata`)
            .then(res => {
                let data = res["data"];
                let state = data["gamestate"];
                let hint_text = data["hint_text"];
                let hint_exists = data["hint_exists"];
                let time = data["time"];
                if (state == "completed"){ // Slightly hacky way to stop time from updating on the win screen
                    time = this.state.time
                }
                let hint_timer = data["hint_timer"];
                let paused = data["paused"];

                if (hint_exists && (hint_text !== this.state.hint_text))
                {
                    this.setState({
                        'hint_text': hint_text,
                        'hint_exists': hint_exists,
                        'time': time,
                        'hint_timer': hint_timer,
                        'paused': paused,
                        'gamestate': state
                    }); 
                    setTimeout(
                        () => this.removeHint(),
                        data["hint_timer"]*1000
                    );
                    this.playHintAudio();
                }
                else
                {
                    this.setState({
                        'time': time,
                        'paused': paused,
                        'gamestate': state
                    });
                }

                console.log(data);
            });
    }

    removeHint()
    {
        console.log("remove hint");
        this.state.hint_exists = false;
    }

    playHintAudio()
    {
        console.log(`http://${BASE_URL}/playAudio/${HINT_AUDIO_FILE}`)
        axios.post(`http://${BASE_URL}/playAudio/${HINT_AUDIO_FILE}`)
             .then(function (response) {
                 console.log(response);
             })
             .catch(function (error) {
                 console.log(error);
             });
    }

    lowerTime()
    {
        if (!this.state.paused){
            this.setState({"time": this.state.time - 1})
        }
    }

    componentDidMount()
    {
        this.ajaxID = setInterval(
            () => this.checkServerState(),
            TICK_TIME
        );
        this.timer = setInterval(
            () => this.lowerTime(),
            1000
        );
    }

    componentWillUnmount()
    {
        clearInterval(this.ajaxID);
        clearInterval(this.timer)
    }
}
