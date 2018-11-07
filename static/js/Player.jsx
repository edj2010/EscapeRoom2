import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import ReactCountdownClock from 'react-countdown-clock';

let BASE_URL = "localhost:5000";
let TICK_TIME = 5000;

export default class Gameroom extends Component {
    constructor(props){
        super(props);
        this.state = {
            hint_text = "";
            hint_exists = false;
            hint_duration = 0;

            time = 0;
            paused = false;
            
            gamestate = "unstarted"
        };
    }

    render() {
        if (this.state.hint_exists)
        {
            return (
            <div className="Gameroom">
                <p> Hint: {this.state.hint_text} </p>
            </div>
            );
        }
        else
        {
            return (
            <div className="Gameroom">
                <ReactCountdownClock seconds={this.state.time} timeformat={"hms"}/>
            </div>
            );
        }
    }

    checkServerState()
    {
        axios.get(`http://${BASE_URL}/getdata`)
            .then(res => {
                console.log(res["data"]);
                this.setState(res["data"]);
            });
    }

    componentDidMount()
    {
        this.ajaxID = setInterval(
            () => this.checkServerState(),
            TICK_TIME
        );
    }

    componentWillUnmount()
    {
        clearInterval(this.ajaxID);
    }
}
