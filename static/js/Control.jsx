import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import Timer from 'react.timer';
import Graph from 'react-graph-vis';
import vis from 'vis';

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
        } else if(this.state.gameState==="ongoing"){
            return(
                <div>
                    <TimerWrapper time={this.state.time} state={this.props.gameState}/>
                    <PuzzleList/>
                    <PuzzleGraph/>
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
        axios.get(`http://${BASE_URL}/start`)
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
    axios.get(`http://${BASE_URL}/getdata`)
      .then(res => {
        let data = res["data"];
        console.log(data);
        this.setState({time: Number(data["time"]), gameState: data["gamestate"]});
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
        axios.get(`http://${BASE_URL}/nodeStates`)
            .then(res => {
                let data = res["data"];
                console.log(data);
                this.setState(
                    {availablePuzzles: data["active"],
                    solvedPuzzles: data["finished"]});
                });
    }

    completePuzzle(puzzleName){
        axios.get(`http://${BASE_URL}/gameState/${puzzleName}/1`)
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
            <li key={puzzleInfo["id"].toString()}>
                <button onClick={evt => this.completePuzzle(puzzleInfo["name"])}> {puzzleInfo["name"]}</button>
            </li>
        );
        let solvedListItems = this.state.solvedPuzzles.map((puzzleInfo) =>
            <li key={puzzleInfo["id"].toString()}>
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

class PuzzleGraph extends Component {
    constructor(props){
        super(props);
        this.state = {nodes: [], edges: [], active: [], solved: []};
        this.network = {};
        this.setNetworkInstance = this.setNetworkInstance.bind(this);
        this.checkPuzzles = this.checkPuzzles.bind(this);
        this.initializeGraph();
    };

    componentDidMount() {
        this.ajaxID = setInterval(
            () => this.checkPuzzles(),
            TICK_TIME
        )};
    componentWillUnmount() {
        clearInterval(this.ajaxID);
    };

    checkPuzzles(){
        axios.get(`http://${BASE_URL}/nodeStates`)
             .then(res => {
                 let data = res["data"];
                 console.log(data["active"])
                 console.log(data["finished"])

                 // TODO: Make a color nodes function rather than 3 loops
                 for (var solved_node_info of data["finished"]){
                     console.log("solved node");
                     console.log(solved_node_info);
                     var solvedNode = this.network.body.data.nodes.get(solved_node_info.name);
                     console.log(solvedNode);
                     solvedNode.color = {
                         border: '#000000',
                         background: '#DC6E56',
                         highlight: {
                             border: '#2B7CE9',
                             background: '#D2E5FF'
                         }
                     }
                     this.network.body.data.nodes.update(solvedNode);
                 }

                 for (var active_node_info of data["active"]){
                     console.log(active_node_info);
                     var activeNode = this.network.body.data.nodes.get(active_node_info.name);
                     console.log("active node");
                     console.log(activeNode);
                     activeNode.color = {
                         border: '#000000',
                         background: '#79C13A',
                         highlight: {
                             border: '#2B7CE9',
                             background: '#D2E5FF'
                         }
                     }
                     this.network.body.data.nodes.update(activeNode);
                 }
                 for (var inactive_node_info of data["inactive"]){
                     console.log(inactive_node_info);
                     var inactiveNode = this.network.body.data.nodes.get(inactive_node_info.name);
                     console.log("inactive node");
                     console.log(inactiveNode);
                     inactiveNode.color = {
                         border: '#000000',
                         background: '#660066',
                         highlight: {
                             border: '#2B7CE9',
                             background: '#D2E5FF'
                         }
                     }
                     this.network.body.data.nodes.update(inactiveNode);
                 }
             });
    }

    initializeGraph() {
        axios.get(`http://${BASE_URL}/graph`)
             .then(res => {
                 let parsedData = vis.network.convertDot(res["data"]);
                 this.setState({nodes: parsedData.nodes, edges: parsedData.edges});
             })
    }

    setNetworkInstance(nw) {
        this.network = nw;
    };

    completeNode(node) {
        axios.get(`http://${BASE_URL}/gameState/${node.label}/1`);
    }

    render(){
        const options = {
            layout: {
                hierarchical: true
            },
            edges: {
                color: "#000000"
            }
        };

        const events = {
            click: function(event) {
                console.log(event.nodes[0]);
                var clickedNode = this.network.body.data.nodes.get(event.nodes[0]);
                this.completeNode(clickedNode);
                clickedNode.color = {
                    border: '#000000',
                    background: '#DC6E56',
                    highlight: {
                        border: '#2B7CE9',
                        background: '#D2E5FF'
                    }
                };
                this.network.body.data.nodes.update(clickedNode);
            }.bind(this)
        };
        var graph = {nodes: this.state.nodes, edges: this.state.edges};
        return(<Graph graph={graph} options={options} events={events} style={{ height: "640px" }} getNetwork={this.setNetworkInstance}/>)
    };

}
