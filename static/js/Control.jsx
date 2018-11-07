import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import Timer from 'react.timer';

//let BASE_URL = "ogillespie.pythonanywhere.com";
let BASE_URL = "localhost:5000";
let TICK_TIME = 5000;

export default class Control extends Component {
    constructor(props){
        super(props);
        this.state = {
            gameState: "unknown",
            time: "??:??",
            urlPlaying: "None"
        };
    this.checkServerState = this.checkServerState.bind(this);
    };

    render(){
        if(this.state.gameState==="unstarted"){
            return(
                <div>
                    <button onClick={evt =>this.startGame()}>Start Game</button>
                </div>
            );
        } else if(this.state.gameState==="start"){
            return(
                <div>
                    <TimerWrapper time={this.state.time} state={this.props.gameState}/>
                    <PuzzleList/>
                </div>
            );
        } else if(this.state.gameState==="completed"){
            return(
                    <div>
                        <p>Room completed with {Math.floor(this.state.time)} seconds left </p>
                        <button onClick={evt =>this.resetRoom()}>Reset Room</button>
                    </div>);
        } else if(this.state.gameState==="lost"){
            return(
                    <div>
                        <p>Room failed </p>
                        <button onClick={evt =>this.resetRoom()}>Reset Room</button>
                    </div>);
        } else if(this.state.gameState==="unknown"){
            return(<p>Loading control panel...</p>);
        }
        else {
            return(<p>Current state not handled. State is {this.state.gameState}</p>);
        }
    }

    startGame() {
        axios.get(`http://${BASE_URL}/controls/start`)
            .then(function (response) {
                console.log(response);
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    resetRoom() {
        axios.get(`http://${BASE_URL}/controls/restart`)
            .then(function (response) {
                console.log(response);
            })
            .catch(function (error) {
                console.log(error);
            });
    }
            

    componentDidMount() {
        this.ajaxID = setInterval(
        () => this.checkServerState(),
        TICK_TIME
    )};
    componentWillUnmount() {
        clearInterval(this.ajaxID);
    }

  checkServerState(){
    console.log("getting data");
    axios.get(`http://${BASE_URL}/display`)
      .then(res => {
        let data = res["data"];
        let newState = data["state"];
        this.setState({time: Number(data["time"]),
                        urlPlaying: data["url"],
                        gameState: newState});
      });
    }
  }

class TimerWrapper extends Component {
    render(){
        if(this.props.time==="??:??"){
            return (<p>{"Fetching Time"}</p>);
        } else if(this.props.state==="unstarted") {
            return (<p>{"Waiting for the game to start"}</p>);
        } else {
            return (
                <div>
                    <Timer countDown startTime={this.props.time}/>
                    <p>{" Seconds left!"}</p>
                </div>
            );
        }
    }
}

class PuzzleList extends Component {
    constructor(props){
        super(props);
        this.state = {
            availablePuzzles: [],
            solvedPuzzles: []
        };
    this.checkPuzzles = this.checkPuzzles.bind(this);
    }    

    componentDidMount() {
        this.ajaxID = setInterval(
        () => this.checkPuzzles(),
        TICK_TIME
    )};
    componentWillUnmount() {
        clearInterval(this.ajaxID);
    }

    checkPuzzles(){
        console.log("check available puzzles");
        axios.get(`http://${BASE_URL}/puzzles/available`)
            .then(res => {
                let data = res["data"];
                console.log(data);
                this.setState(
                    {availablePuzzles: data});
                });
        axios.get(`http://${BASE_URL}/puzzles/solved`)
            .then(res => {
                let data = res["data"];
                console.log(data);
                this.setState(
                    {solvedPuzzles: data});
                });
    }

    completePuzzle(puzzleName){
        axios.get(`http://${BASE_URL}/puzzles/complete/${puzzleName}`)
        .then(function (response) {
            console.log(response);
        })
        .catch(function (error) {
            console.log(error);
        });
    };

    // TODO: Do we need to unmount all the axios calls?

    render(){
        let listItems = this.state.availablePuzzles.map((puzzleInfo) =>
            <li key={puzzleInfo["puzzleID"].toString()}>
                <button onClick={evt => this.completePuzzle(puzzleInfo["name"])}> {puzzleInfo["name"]}</button>
            </li>
        );
        let solvedListItems = this.state.solvedPuzzles.map((puzzleInfo) =>
            <li key={puzzleInfo["puzzleID"].toString()}>
                <p> {puzzleInfo["name"]}</p>
            </li>
        );
        return(
            <div>
                <p>Unsolved Puzzles</p>
                <ul>{listItems}</ul>
                <p>Solved Puzzles</p>
                <ul>{solvedListItems}</ul>
            </div>
        );
    }

}
