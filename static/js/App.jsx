import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import screenfull from 'screenfull';
import ReactPlayer from 'react-player';
//import logo from './logo.svg';
import axios from 'axios';
import ReactCountdownClock from 'react-countdown-clock';
//import './App.css';

let BASE_URL = "ogillespie.pythonanywhere.com";
//let BASE_URL = "localhost:5000";
let TICK_TIME = 5000;

export default class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      "state": "unstarted"
    };
  }
  render() {
    switch (this.state["state"]){
      case "video":
        return (
          <div className="App">
            <Player url={"https://www.youtube.com/watch?v=V0HCZ4YGqbw"}/>
          </div>
        );
      case "start":
        return (
          <div className="App">
            <ReactCountdownClock seconds={this.state.time} timeformat={"hms"}/>
          </div>
        );
      case "completed":
        return (
          <div className="App">
            <p> Congrats! You finished with {Math.floor(this.state.time / 60)}:{Math.floor(this.state.time % 60)} left</p>
          </div>
        );
      case "lost":
        return (
        <div className="App">
            <p>Tough Luck. S.H.O.W.E.R. successfully retrieved the legendary hammer before you could stop them.</p>
        </div>
        );
      case "unstarted":
      default:
        return(
          <div className="App">
            <p> Welcome to our escape room. Please wait for the game to start </p>
          </div>
        );
    }
  }

  checkServerState(){
    axios.get(`http://${BASE_URL}/display`)
      .then(res => {
        console.log(res["data"]);
        let data = res["data"];
        let newState = data["state"];
        if (newState !== this.state["state"]){
          this.setState({ "state": newState});
          this.setState({"time": data["time"]});
        };
      });
  }

  componentDidMount() {
    this.ajaxID = setInterval(
      () => this.checkServerState(),
      TICK_TIME
    );
  }

  componentWillUnmount() {
    clearInterval(this.ajaxID);
  }
}


class Player extends React.Component{
  constructor(props){
    super(props);
  }

  render() {
    return (
      <div>
        <ReactPlayer
          ref={'player'}
          url={this.props.url}
          //eslint-disable-next-line
          width={screen.width - 10}
          //eslint-disable-next-line
          height={screen.height- 10}
          playing
        />
      </div>
    )
  }
};

