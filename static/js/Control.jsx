import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import Timer from 'react.timer';
import Graph from 'react-graph-vis';
import ReactTable from 'react-table';
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
        this.checkServerState();
    };

    render(){
        if(this.state.gameState==="unstarted"){
            return(
                <div>
                    <button onClick={evt =>this.startGame()}>Start Game</button>
                    <HeartBeatTable/>
                </div>
            );
        } else if(this.state.gameState==="ongoing"){
            return(
                <div>
                    <TimerWrapper time={this.state.time} state={this.props.gameState}/>
                    <PuzzleGraph/>
                    <HintSender/>
                    <HeartBeatTable/>
                </div>
            );
        } else if(this.state.gameState==="completed"){
            return(
                    <div>
                        <p>Room completed with {Math.floor(this.state.time)} seconds left </p>
                        <button onClick={evt =>this.resetRoom()}>Reset Room</button>
                        <HeartBeatTable/>
                    </div>);
        } else if(this.state.gameState==="out_of_time"){
            return(
                    <div>
                        <p>Room failed </p>
                        <button onClick={evt =>this.resetRoom()}>Reset Room</button>
                        <HeartBeatTable/>
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
        this.checkPuzzles();
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
        axios.get(`http://${BASE_URL}/nodeStates`)
            .then(res => {
                let data = res["data"];
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

class HeartBeatTable extends Component {
    constructor(props){
        super(props);
        this.state = {heartbeats: []};
        this.checkHeartbeats = this.checkHeartbeats.bind(this);
        this.checkHeartbeats();
    }

    componentDidMount(){
        this.ajaxID = setInterval(
            () => this.checkHeartbeats(),
            TICK_TIME
        )
    };
    componentWillUnmount(){
        clearInterval(this.ajaxID);
    };

    checkHeartbeats(){
        axios.get(`http://${BASE_URL}/heartbeats`)
             .then(res => {
                let heartbeats = res["data"];
                let currentTime = Math.round((new Date()).getTime() / 1000);
                let relativeHeartbeats = heartbeats.map(heartbeat => {
                    let relativeHeartbeat = {};
                    relativeHeartbeat["name"] = heartbeat.name;
                    relativeHeartbeat["time"] = Math.round(currentTime - heartbeat.time);
                    return relativeHeartbeat;
                });
                this.setState({"heartbeats": relativeHeartbeats});
             }
        );
    }

    render(){
        return (
            <div>
                <ReactTable
                    data={this.state.heartbeats}
                    columns = {[
                        {
                            Header: 'Name',
                            accessor: 'name',
                            width: 200
                        }, {
                            Header: 'Seconds since last ping',
                            accessor: 'time',
                            width: 200
                        }
                    ]}
                    minRows={0}
                    showPagination={false}
                    defaultSorted={[
                        {
                            id: "time",
                            desc: true
                        }
                    ]}
                />
            </div>
        );
    }
}

class HintSender extends Component {
    constructor(props){
        super(props);
    }

    render(){
        return (
            <form action="/setHint" method="post">
                <div>
                    Message:
                    <input type="text" id="message" name="hint_message"/>
                </div>
                <div>
                    Seconds Displayed:
                    <input type="number" id="time" name="hint_timer" defaultValue="30" min="10"/>
                </div>
                <div className="button">
                    <button type="submit">Send Hint</button>
                </div>
            </form>
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
        this.checkPuzzles();
    };

    componentDidMount() {
        this.ajaxID = setInterval(
            () => this.checkPuzzles(),
            TICK_TIME
        );
    };
    componentWillUnmount() {
        clearInterval(this.ajaxID);
    };

    checkPuzzles(){
        axios.get(`http://${BASE_URL}/nodeStates`)
             .then(res => {
                 let data = res["data"];

                 // TODO: Make a color nodes function rather than 3 loops
                 for (var solved_node_info of data["finished"]){
                     var solvedNode = this.network.body.data.nodes.get(solved_node_info.name);
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
                     var activeNode = this.network.body.data.nodes.get(active_node_info.name);
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
                     var inactiveNode = this.network.body.data.nodes.get(inactive_node_info.name);
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

    toggleNode(node) {
        axios.get(`http://${BASE_URL}/gameState/${node.label}/toggle`);
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
                if (event.nodes.length != 0){
                    var clickedNode = this.network.body.data.nodes.get(event.nodes[0]);
                    this.toggleNode(clickedNode);
                    clickedNode.color = {
                        border: '#000000',
                        background: '#DC6E56',
                        highlight: {
                            border: '#2B7CE9',
                            background: '#D2E5FF'
                        }
                    };
                    this.network.body.data.nodes.update(clickedNode);
                }
            }.bind(this)
        };
        var graph = {nodes: this.state.nodes, edges: this.state.edges};
        return(<Graph graph={graph} options={options} events={events} style={{ height: "640px" }} getNetwork={this.setNetworkInstance}/>)
    };

}
