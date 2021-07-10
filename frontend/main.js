const svgns = "http://www.w3.org/2000/svg"
const video = document.getElementById('video')
var displaySize = { width: video.offsetWidth, height: video.offsetHeight }

const sizeFaceBuffer = 20
const timeDelation = 300
const max_len = 40
var labelFace = []
var infoPool = new Map();
var face_state = new Map();
var faceBuffer = []
var faceMatcher

// server ip
const url = ""


function httpPost(theUrl, data)
{
    var xmlHttp = new XMLHttpRequest()
    xmlHttp.open( "POST", theUrl, false )
    xmlHttp.send( JSON.stringify(data) )
    return JSON.parse(xmlHttp.responseText)
}


Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri(''),
  faceapi.nets.faceLandmark68Net.loadFromUri(''),
  faceapi.nets.faceRecognitionNet.loadFromUri(''),
  faceapi.nets.faceExpressionNet.loadFromUri('')
]).then(startVideo)


function CreateSvgFace(detect_item,  color) {

  let x = detect_item.alignedRect.box.left
  let y = detect_item.alignedRect.box.top
  let height = detect_item.alignedRect.box.height
  let width = detect_item.alignedRect.box.width
  let label = MathInPool(detect_item)
  let text_arr = UserInfo(label)
  
  rect = document.createElementNS(svgns, 'rect')
  rect.setAttributeNS(null, 'x', x)
  rect.setAttributeNS(null, 'y', y)
  rect.setAttributeNS(null, 'height', height)
  rect.setAttributeNS(null, 'width', width)
  rect.setAttributeNS(null, "fill-opacity", "0")
  rect.setAttributeNS(null, "stroke-width", "5")
  rect.setAttributeNS(null, "onclick", `SwitchState('${label}')`)
  
  text = document.createElementNS(svgns, 'text')
  text.setAttributeNS(null, 'id', "user_info")
  text.setAttributeNS(null, 'x', x)
  text.setAttributeNS(null, 'y', y)

  if (face_state.get(label) === 0){
    text.setAttributeNS(null, "class", "title")
  }

  text_arr.forEach(
    (line) => {
      row = document.createElementNS(svgns, 'tspan')
      row.setAttributeNS(null, 'x', x + height / 2)
      row.setAttributeNS(null, 'dy', "1em")
      row.textContent = line
      text.appendChild(row)
    }
  )

  document.getElementById('svgImg').appendChild(text)

  document.getElementById('svgImg').appendChild(rect)
}


function ClearSvg() {
  while (svgImg.firstChild) {
    svgImg.removeChild(svgImg.firstChild);
  }
}

function SwitchState(link) {
  if (face_state.get(link) === 0){
    face_state.set(link, 1)
  } else {
    face_state.set(link, 0)
  }
}


function UserInfo(link){
  let data_from_link = infoPool.get(link)
  text = []
  if (face_state.get(link) === 1){
    data_from_link.grades.forEach((line) => text.push(line[0].slice(0, max_len - line[1].length + 1) + "...: " + line[1]))
    return text
  } else {
    text.push(data_from_link.group + " " + data_from_link.name)
    return text
  }
}


function MathInPool(face){
  if (faceMatcher && labelFace.includes(faceMatcher.findBestMatch(face.descriptor).label)) {
    return faceMatcher.findBestMatch(face.descriptor).label
  } else {
    AddImageToPool(face)
  }
}


function AddImageToPool(face){
  if (labelFace.length == faceBuffer.length) {labelFace.push(GetLabel(face))}
  faceBuffer.push(new faceapi.LabeledFaceDescriptors(labelFace[faceBuffer.length], [face.descriptor]))
  
  faceMatcher = new faceapi.FaceMatcher(faceBuffer)
  console.log("Detect new face")
}


function GetLabel(face){
  let f_label = "User" + labelFace.length
  infoPool.set(f_label, httpPost(url, face.descriptor))
  face_state.set(f_label, 0)
  return f_label
}



async function startVideo() {
  var devices
  await navigator.mediaDevices.enumerateDevices().then(d => devices = d)
  const videoDevices = devices.filter(device => device.kind === 'videoinput')

  console.log(videoDevices)

  navigator.mediaDevices.getUserMedia({ video: {deviceId: videoDevices[0].deviceId}, audio: false},).then(function(stream) {
    let video = document.getElementById('video');
    if ("srcObject" in video) {
      video.srcObject = stream
    } else {
      video.src = window.URL.createObjectURL(stream)
    }
});
  video.play();
}


video.addEventListener('play', () => {
  setInterval(async () => {
    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceDescriptors()
    displaySize = { width: video.offsetWidth, height: video.offsetHeight }

    svgImg.setAttributeNS(null, "width", video.offsetWidth)
    svgImg.setAttributeNS(null, "height", video.offsetHeight)

    resizedDetections = faceapi.resizeResults(detections, displaySize)
    ClearSvg()
    resizedDetections.forEach(element => CreateSvgFace(element))
  }, timeDelation)
})