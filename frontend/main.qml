import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Dialogs
import QtQml
import QtQuick.Layouts
import QtMultimedia

import "."


ApplicationWindow {
    MediaDevices {
        id: devices
    }
    id: mainrect
    //color: Constants.backgroundColor
    width: manager.config["graphics"]["window_size"]["width"]
    height: manager.config["graphics"]["window_size"]["height"]
    visible: true
    title: qsTr("Dataset generator")

    // temp array for 1st step
    property var name_list: manager.name_list

    Loader {
        id: mainLoader
        visible: true
        source: "mainview.qml"
        anchors.fill: parent
        property int loader_prop_index
        onLoaded: console.log("page is loaded: ", source)
    }

    Connections {
        target: mainLoader.item
        ignoreUnknownSignals: true
        function onGotoStep1() {
            mainLoader.source = "step 1/list.qml"
        }
        function onGotoStep2() {
            mainLoader.source = "step 2/dir.qml"
            console.log("page 2")
        }
        function onGotoStep3() {
            mainLoader.source = "step 3/dir.qml"
            console.log("page 3")
        }
        function onGotoMainView() {
            mainLoader.source = "mainview.qml"
        }
        function onGotoChoosingDir() {
            mainLoader.source = "step 1/dir.qml"
        }
        function onGotoCamera() {
            mainLoader.source = "step 1/camera.qml"
        }
        function onMakeSnapshoot(name) {
            // name snapshot

            //return step1camera.index
        }
        function onGotoThreshold() {
            manager.hsStatus = 0
            mainLoader.source = "step 2/threshold.qml"
        }
        function onGotoBacks() {
            mainLoader.source = "step 3/backs.qml"
        }
        function onGotoGeneration() {
            mainLoader.source = "step 3/generation.qml"
        }
        function onGotoPhotoNum() {
            mainLoader.source = "step 3/photo_num.qml"
        }
        /*onLoadArray: {
            item.getArray(mainrect.firstStepArray)
        }*/
    }
}
